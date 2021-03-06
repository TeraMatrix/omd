#!/usr/bin/env python
#-*- encoding: utf-8 -*-
#
# Copyright 2010-2012 Gerhard Lausser.
# This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

import os
import re
import logging
import shutil
import tempfile
from copy import copy
import subprocess
import coshsh
from coshsh.datasource import Datasource, DatasourceNotAvailable
from coshsh.datarecipient import Datarecipient, DatarecipientNotAvailable
from coshsh.host import Host
from coshsh.application import Application
from coshsh.contactgroup import ContactGroup
from coshsh.contact import Contact
from coshsh.monitoringdetail import MonitoringDetail
from coshsh.util import compare_attr

logger = logging.getLogger('coshsh')

def __ds_ident__(params={}):
    if compare_attr("type", params, "atomic"):
        return AtomicRecipient
    if compare_attr("type", params, "remote_atomic"):
        return RemoteAtomicRecipient


class AtomicRecipient(coshsh.datarecipient.Datarecipient):
    def __init__(self, **kwargs):
        self.name = kwargs["name"]
        self.objects_dir = kwargs["objects_dir"]
        self.items = kwargs.get("items", None)

    def inventory(self):
        logger.info('count items')
        if self.items:
            for item in self.items.split(','):
                if item in self.objects:
                    logger.info('count %d %s' % (len(self.objects[item]), item))

    def prepare_target_dir(self):
        logger.info("recipient %s objects_dir %s" % (self.name, self.objects_dir))
        try:
            os.mkdir(self.objects_dir)
        except Exception:
            # will not have been removed with a .git inside
            pass

    def cleanup_target_dir(self):
        # do not remove anything, because this recipient writes files
        # which are constantly in use
        pass

    def output(self, filter=None, objects={}):
        logger.info('write items to datarecipients object_dir %s' % self.objects_dir)
        self.inventory()
        if self.items:
            for item in self.items.split(','):
                if item in self.objects:
                    logger.info("writing %s atomic ..." % item)
                    for itemobj in self.objects[item].values():
                        self.item_write_config(itemobj, self.objects_dir, '')
        self.count_after_objects()

    def item_write_config(self, obj, dynamic_dir, objtype):
        my_target_dir = os.path.join(dynamic_dir, objtype)
        if not os.path.exists(my_target_dir):
            os.makedirs(my_target_dir)
        for file in obj.config_files:
            content = obj.config_files[file]
            my_target_file = os.path.join(my_target_dir, file)
            with open(my_target_file+'_coshshtmp', "w") as f:
                f.write(content)
                os.fsync(f)
            os.rename(my_target_file+'_coshshtmp', my_target_file)

class RemoteAtomicRecipient(AtomicRecipient):
    def __init__(self, **kwargs):
        self.name = kwargs["name"]
        self.objects_dir = kwargs["objects_dir"]
        self.items = kwargs.get("items", None)
        self.remote = kwargs.get("hostname", None)

    def prepare_target_dir(self):
        logger.info("recipient %s objects_dir %s" % (self.name, self.objects_dir))
        status, stdout, stderr = self.process("ssh -q %s mkdir -p %s" % (self.remote, self.objects_dir))
        if not status:
            raise DatarecipientNotAvailable
        # sollte ueberfluessig sein, da rsync atomic genug ist
        #status, stdout, stderr = self.remote("ssh -q %s mktemp" % (self.remote, self.objects_dir)):
        #if not status:
        #    raise DatarecipientNotAvailable
        #else:
        #    self.rem_tempdir = stdout

    def output(self, filter=None, objects={}):
        if filter:
            for f in [filt.strip() for filt in filter.split(',')]:
                if f.startswith('hostname='):
                    self.trapdest = f.replace("hostname=", "")
        if self.remote == None:
            logger.error('remote atomic needs a valid hostname')
            raise DatarecipientNotAvailable

        local_tempdir = tempfile.mkdtemp()
        logger.info('write items to temporary local object_dir %s' % local_tempdir)
        self.inventory()
        if self.items:
            for item in self.items.split(','):
                if item in self.objects:
                    logger.info("writing %s atomic ..." % item)
                    for itemobj in self.objects[item].values():
                        self.item_write_config(itemobj, local_tempdir, '')
        logger.info('copy items to object_dir %s:%s' % (self.remote, self.objects_dir))
        status, stdout, stderr = self.process("rsync -ac %s/ %s:%s" % (local_tempdir, self.remote, self.objects_dir))
        if not status:
            shutil.rmtree(local_tempdir)
            raise DatarecipientNotAvailable
        else:
            shutil.rmtree(local_tempdir)

    def process(self, command):
        try:
            stdout = "connecting..."
            stderr = "connecting..."
            process = subprocess.Popen(command,
                shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            stdout, stderr = process.communicate()
            status = process.poll()
            if status != 0:
                raise DatarecipientNotAvailable
        except Exception, e:
            logger.error("output stdout " + stdout)
            logger.error("output stderr " + stderr)
            return False, stdout, stderr
        else:
            return True, stdout, stderr


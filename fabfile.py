# -*- coding: utf-8 -*-
from fabric.context_managers import cd
from fabric.contrib.files import exists
from fabric.operations import run
from fabric.state import env

__author__ = 'zhouqi'

def keke():
    global env
    env.hosts = '45.78.57.204'
    env.port = 28243
    env.user = 'keke'


def test():
    run('ls -a')

def deploy():
    if not exists('~/work/pomelo_api'):
        with cd('~/work/'):
            run('git clone git@github.com:bitwolaiye/pomelo_api.git')
    with cd('~/work/pomelo_api'):
        run('git checkout develop')
        run('git pull')


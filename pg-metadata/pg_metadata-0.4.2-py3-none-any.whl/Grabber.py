#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import shutil
from multiprocessing import Pool
from pg_metadata.Database import Database

class Grabber():
    def __init__(self, connect, target_path, exclude_schemas=[]):
        assert connect is not None
        assert isinstance(connect, dict)
        assert len(connect.keys()) > 0

        assert target_path is not None
        assert isinstance(target_path, str)
        assert len(target_path) > 0

        self.TargetPath     = target_path
        self.ExcludeSchemas = exclude_schemas or []
        self.Database       = Database(connect, self.ExcludeSchemas)

    def CreatePath(self, schema_name, folder_name):
        schema_path = '/'.join([self.TargetPath, schema_name])
        if not os.path.exists(schema_path):
            os.mkdir(schema_path)

        folder_path = '/'.join([schema_path, folder_name])
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)

        return folder_path

    def GetPath(self, schema_name, folder_name, file_name):
        folder_path = self.CreatePath(schema_name, folder_name)
        file_name += '.sql'
        file_name = '/'.join([folder_path, file_name])
        return file_name

    def WriteTable(self, table):
        file_name = self.GetPath(table.Schema, table.Folder, table.Name)
        with open(file_name, 'w', encoding='utf-8') as wf:
            wf.write(table.QueryDDL())

    def WriteFunction(self, function):
        file_name = self.GetPath(function.Schema, function.Folder, function.Name)
        with open(file_name, 'w', encoding='utf-8') as wf:
            wf.write(function.QueryDDL())

    def WriteView(self, view):
        file_name = self.GetPath(view.Schema, view.Folder, view.Name)
        with open(file_name, 'w', encoding='utf-8') as wf:
            wf.write(view.QueryDDL())

    def WriteSequence(self, sequence):
        file_name = self.GetPath(sequence.Schema, sequence.Folder, sequence.Name)
        with open(file_name, 'w', encoding='utf-8') as wf:
            wf.write(sequence.QueryDDL())

    def WriteForeignServer(self, server):
        file_name = self.GetPath(server.Schema, server.Folder, server.Name)
        with open(file_name, 'w', encoding='utf-8') as wf:
            wf.write(server.QueryDDL())

    def WriteForeignTable(self, table):
        file_name = self.GetPath(table.Schema, table.Folder, table.Name)
        with open(file_name, 'w', encoding='utf-8') as wf:
            wf.write(table.QueryDDL())

    def CreateFolders(self):
        if os.path.exists(self.TargetPath):
            shutil.rmtree(self.TargetPath)
        os.mkdir(self.TargetPath)

        for k,tbl in self.Database.Tables.items():
            self.CreatePath(tbl.Schema, tbl.Folder)

        for k,fnc in self.Database.Functions.items():
            self.CreatePath(fnc.Schema, fnc.Folder)

        for k,seq in self.Database.Sequences.items():
            self.CreatePath(seq.Schema, seq.Folder)

        for k,vw in self.Database.Views.items():
            self.CreatePath(vw.Schema, vw.Folder)

        for k,fs in self.Database.ForeignServers.items():
            self.CreatePath(fs.Schema, fs.Folder)

        for k,ft in self.Database.ForeignTables.items():
            self.CreatePath(ft.Schema, ft.Folder)

    def Grab(self):
        self.Database.Parse()
        self.CreateFolders()

        pool = Pool(processes=8)
        pool.map(self.WriteTable,           [v for k,v in self.Database.Tables.items()])
        pool.map(self.WriteFunction,        [v for k,v in self.Database.Functions.items()])
        pool.map(self.WriteView,            [v for k,v in self.Database.Views.items()])
        pool.map(self.WriteSequence,        [v for k,v in self.Database.Sequences.items()])
        pool.map(self.WriteForeignServer,   [v for k,v in self.Database.ForeignServers.items()])
        pool.map(self.WriteForeignTable,    [v for k,v in self.Database.ForeignTables.items()])

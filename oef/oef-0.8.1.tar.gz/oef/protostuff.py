from google.protobuf.message import Message

import json

def protoToSomething(pb, fn):
    #print("protoToSomething:", fn)
    val = getattr(pb, fn)
    if isinstance(val, Message):
        return protoToDict(val)
    return val

def protoToDict(pb):
    r = {}

    oneofs = set([
        d.containing_oneof.name
        for d
        in pb.DESCRIPTOR.fields_by_name.values()
        if d.containing_oneof != None
    ])

    otherfields = set([
        k
        for k,d
        in pb.DESCRIPTOR.fields_by_name.items()
        if d.containing_oneof == None
    ])

    for oneof in oneofs:
        try:
            theone = pb.WhichOneof(oneof)
            if theone != None:
                r[theone] = protoToSomething(pb, theone)
        except Exception as ex:
            raise ValueError("while assigning {}/{}, {}".format(oneof, theone, ex))

    for fn in otherfields:
        try:
            r[fn] = protoToSomething(pb, fn)
        except Exception as ex:
            raise ValueError("ERROR: while assigning {}, {}".format(fn, ex))

    return r


def valueToProtoField(pb, fn, data, path=""):
    target = None
    try:
        path="{}.{}".format(path,fn)
        #print("valueToProtoField -- about to assign {} to {} ({})".format(type(data), path, type(pb)))

        if data == None:
            return
        if isinstance(data, Message):
            getattr(pb, fn).CopyFrom(data)
            return
        if type(data) == list:
            assignList(getattr(pb, fn), data, path="?"+path)
            return
        if hasattr(data, 'to_dict') and callable(getattr(data, 'to_dict')):
            #print("DOING to_dict on a {}", type(data))
            data = data.to_dict()
            #print("RESULT: {} ({})".format(data, type(data)))
        if type(data) == dict:
            target = getattr(pb, fn)
            assignDict(target, data, path=path)
            return

        if not fn in pb.DESCRIPTOR.fields_by_name.keys():
            raise ValueError("while setting fn={}, not found".format(fn))

        setattr(pb, fn, data)
    except Exception as ex:
        print("ERROR: doing valueToProtoField: {} {} {} := {} => {} {}".format(path, type(target), target,type(data), ex, type(ex)))
        raise ex

def assignList(target, listdata, path=""):
    try:
        #print("assignList -- about to assign {} to {} ({})".format(type(listdata), path, type(target)))
        for i,data in enumerate(listdata):
            path="{}[{}]".format(path,i)
            if hasattr(data, 'to_dict') and callable(getattr(data, 'to_dict')):
                data = data.to_dict()
            if type(data) == list:
                subtarget = target.add()
                assignList(subtarget, data, path="!"+path)
            elif type(data) == dict:
                subtarget = target.add()
                assignDict(subtarget, data, path=path)
            else:
                target.append(data)
    except Exception as ex:
        print("ERROR: doing assignList: {} {} {} := {} => {} {}".format(path, type(target), target,type(data), ex, type(ex)))
        raise ex

def assignDict(pb, data, path=""):
    try:
        #print("assignDict -- about to assign {} to {} {} ({})".format(type(data), path, pb, type(pb)))
        if not isinstance(data, dict):
            if hasattr(data, 'to_dict') and callable(getattr(data, 'to_dict')):
                data = data.to_dict()
        if len(data) == 0:
            pb.CopyFrom(type(pb)())
        else:
            for fn,v in data.items():
                #print("assignDict fn={}, v={}".format(fn, type(v)))
                if fn == None:
                    continue
                valueToProtoField(pb, fn, v, path=path)
    except Exception as ex:
        print("ERROR: doing assignList: {} := {} => {} {}".format(path, type(data), ex, type(ex)))
        raise ex

def dictToProto(pb, data):
    try:
        assignDict(pb, data, path="")
    except Exception as ex:
        raise(ex)

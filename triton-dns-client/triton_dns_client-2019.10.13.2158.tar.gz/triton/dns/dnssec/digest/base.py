from bitstring import BitArray




class Digest:
    id: int

    @classmethod
    def hash_key(cls, key_resource_record):
        """
        Hashes DNSKEY resource record (name + rdata)
        :param key_resource_record:
        :return:
        """
        from triton.dns.message.domains.domain import Domain
        h = cls.hasher.new()
        h.update(
            BitArray(bin=Domain.sub_encode(key_resource_record.name) + key_resource_record.rdata.Binary.full).bytes)
        return h.digest()

    @classmethod
    def by_id(cls, id):
        """
        Finds Digest type by its id
        :param id:
        :return:
        """
        for subclass in Digest.__subclasses__():
            if subclass.id == id:
                return subclass
        else:
            raise Exception('Unknown digest id')

    @classmethod
    def verify_key_rr(cls, key_resource_record, ds_resource_record):
        """
        Verifies that DNSKEY resource record matches DS resource record on parent
        :param key_resource_record:
        :param ds_resource_record:
        :return:
        """
        assert key_resource_record.rdata.key_tag == ds_resource_record.rdata.key_tag, 'Key tags mismatch'
        hashed_key = cls.hash_key(key_resource_record)
        if ds_resource_record.rdata._digest == hashed_key:
            return True
        return False

    @classmethod
    def verify_from_ds(cls, key_resource_record, ds_resource_record):
        return Digest.by_id(ds_resource_record.rdata._digest_type).verify_key_rr(key_resource_record,
                                                                                 ds_resource_record)

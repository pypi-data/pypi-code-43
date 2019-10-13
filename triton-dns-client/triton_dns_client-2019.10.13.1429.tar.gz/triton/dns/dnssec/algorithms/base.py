import datetime

from Cryptodome.Hash import SHA
from bitstring import BitArray


class ValidationError(Exception):
    pass


class Algorithm:
    id = 0
    hasher: SHA

    def verify_algorithm(f):
        def wrapper(cls, key_rr, rrset, rrsig):
            assert key_rr.rdata._algorithm == cls.id
            assert rrsig.rdata._algorithm == cls.id
            assert rrsig.rdata.key_tag == key_rr.rdata.key_tag
            return f(cls, key_rr, rrset, rrsig)

        return wrapper

    def validate_signature_time(f):
        def wrapper(cls, key_rr, rrset, rrsig):
            now = datetime.datetime.now(tz=datetime.timezone.utc)
            if rrsig.rdata.signature_expiration < now:
                raise ValidationError('Signature expired')
            elif rrsig.rdata.signature_inception > now:
                raise ValidationError('Signature inception time is in future')
            return f(cls, key_rr, rrset, rrsig)

        return wrapper

    def sort_rrset(f):
        def wrapper(cls, key_rr, rrset, rrsig):
            if len(set([x.name for x in rrset])) == 1:  # If all answers name match then sort rr by rdata
                rrset = sorted(rrset, key=lambda x: x.rdata.Binary.full)
            return f(cls, key_rr, rrset, rrsig)
        return wrapper

    @classmethod
    @verify_algorithm
    @validate_signature_time
    @sort_rrset
    def verify_rrset(cls, key_rr, rrset, rrsig):
        signer = cls.construct_signer(key_rr=key_rr)
        hash = cls.hasher.new()
        hash.update(BitArray(bin=rrsig.rdata.Binary.without_signature).bytes)
        for rr in rrset:
            hash.update(rr.Binary.full_canonical_bytes)
        return signer.verify(hash, rrsig.rdata._signature)

    @classmethod
    def construct_signer(cls, key_rr):
        pass  # TODO need info on ECC, DSA, ED algorithms public key

    @classmethod
    def find_by_id(cls, id):
        for subtype in Algorithm.__subclasses__():
            for subclass in subtype.__subclasses__():
                if subclass.id == id:
                    return subclass
        else:
            raise Exception('Unknown algorithm id')

    @classmethod
    def find_by_name(cls, name: str):
        for subtype in Algorithm.__subclasses__():
            for subclass in subtype.__subclasses__():
                if subclass.__name__.lower() == name.lower():
                    return subclass
        else:
            raise Exception(f'Unknown algorithm name {name}')

    @classmethod
    def sign_rrset(cls, key, rrset):
        pass

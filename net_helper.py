import dns.resolver
import socket


def get_host_by_name(domain):
    """
    Return the IP address for a host.
    @source https://www.tutorialspoint.com/python-program-to-find-the-ip-address-of-the-client

    :param domain:
    :return: IP address
    """

    try:
        return socket.gethostbyname(domain)
    except:
        return None


def get_mx_records(domain):
    """
    Return MX records for a host

    :param domain:
    :return:
    """

    try:
        # get mx records
        # https://stackoverflow.com/a/4339305/1565790
        # https://www.dnspython.org/examples/
        # https://kernel.sr/find-mx-records-in-large-batches-with-python/hharpal/

        mx_records = dns.resolver.resolve(domain, 'MX')
        # pprint(len(mx_records))

        # ###############################################
        # DEBUG - Print out all (attribute:value) pairs #
        # ###############################################
        # Possible attributes:
        #
        # covers   --   <bound method Rdata.covers of <DNS IN MX rdata: 10 aspmx.l.google.com.>>
        # exchange   --   aspmx.l.google.com.
        # extended_rdatatype   --   <bound method Rdata.extended_rdatatype of <DNS IN MX rdata: 10 aspmx.l.google.com.>>
        # from_text   --   <bound method MXBase.from_text of <class 'dns.rdtypes.ANY.MX.MX'>>
        # from_wire_parser   --   <bound method MXBase.from_wire_parser of <class 'dns.rdtypes.ANY.MX.MX'>>
        # preference   --   10
        # rdclass   --   RdataClass.IN
        # rdcomment   --   None
        # rdtype   --   RdataType.MX
        # replace   --   <bound method Rdata.replace of <DNS IN MX rdata: 10 aspmx.l.google.com.>>
        # to_digestable   --   <bound method Rdata.to_digestable of <DNS IN MX rdata: 10 aspmx.l.google.com.>>
        # to_generic   --   <bound method Rdata.to_generic of <DNS IN MX rdata: 10 aspmx.l.google.com.>>
        # to_text   --   <bound method MXBase.to_text of <DNS IN MX rdata: 10 aspmx.l.google.com.>>
        # to_wire   --   <bound method Rdata.to_wire of <DNS IN MX rdata: 10 aspmx.l.google.com.>>
        # get_mx_records:  None
        # for rdata in mx_records:
        #     pprint(rdata)
        #     for k in dir(rdata):
        #         if k[0] != '_':
        #             # https://stackoverflow.com/a/13595755/1565790
        #             print(k, '  --  ', getattr(rdata, k))
        #     return

        return [str(x.exchange) for x in mx_records]
    except:
        return None


def validate_domain(domain):
    print(f'{domain}'.ljust(25), end='')

    # get domain ip or mx records
    ip = get_host_by_name(domain)

    if not ip:
        print('!get_host_by_name'.ljust(20), end='')
        if not get_mx_records(domain):
            print('!get_mx_records'.ljust(20), end='')
            return False

    print(f'{ip}', end='')

    return True


def get_domain(email):
    return email[email.rfind('@') + 1:] if email.rfind('@') > -1 else None

from net_helper import get_host_by_name, get_mx_records


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
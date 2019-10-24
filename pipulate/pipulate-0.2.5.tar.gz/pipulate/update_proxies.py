def Main():
    from random import shuffle
    from itertools import cycle
    from datetime import datetime
    import requests
    from time import sleep

    common_terms = list()
    try:
        with open('words.txt') as proxy_words:
            for line in proxy_words:
                common_terms.append(line[:-1])
    except:
        print("Put your long list of words.txt in repo folder")
        raise SystemExit()

    common_agents = list()
    try:
        with open('useragents.txt') as proxy_words:
            for line in proxy_words:
                common_agents.append(line[:-1])
    except:
        print("Put your long list of useragents.txt in repo folder")
        raise SystemExit()

    minimum_seconds = 10
    shuffle(common_terms)
    term_cycler = cycle(common_terms)
    shuffle(common_agents)
    agent_cycler = cycle(common_agents)
    good_proxies = list()
    bad_proxies = list()
    unreachable = list()
    bad_blocks = set()
    good_blocks = set()
    last_used = dict()

    #Grab total list of proxies
    proxies = []
    try:
        with open('proxies.txt', 'r') as f:
            for line in f:
                proxies.append(line.strip())
    except:
        print("Put your list of proxies.txt in repo folder")
        raise SystemExit()

    #Create a set of all the C blocks in use
    block_dict = dict()
    blocks = set()
    staggered = []
    for proxy in proxies:
        block = '.'.join(proxy.split('.')[:3])
        block_dict[proxy] = block
        blocks.add(block)

    #Ensure IPs are highly staggered in list by C block
    staggered = []
    while proxies:
        for block in blocks:
            for index, test_next in enumerate(proxies):
                next_block = '.'.join(test_next.split('.')[:3])
                if block == next_block:
                    staggered.append(test_next)
                    del proxies[index]
                    break

    #Step through staggered list to test proxies for 505 responses
    for x, ip in enumerate(staggered):
        ip = ip.rstrip()
        block = '.'.join(ip.split('.')[:3])
        if block in good_blocks:
            print(x, "White-listing %s based on good block." % ip)
            good_proxies.append(ip)
        elif block not in bad_blocks:
            if block in last_used:
                delta = datetime.now() - last_used[block]
                delta = delta.seconds
                if delta < minimum_seconds:
                    pause = minimum_seconds - delta
                    s = ''
                    if pause > 1:
                        s = 's'
                    print("<< Sleeping %s second%s for block %s >>" % (pause, s, block))
                    sleep(pause)
            last_used[block] = datetime.now()
            proxy = {'http': 'http://'+ip, 'https': 'http://'+ip}
            try:
                term = next(term_cycler)
                agent = next(agent_cycler)
                user_agent = {'User-agent': agent}
                query = 'https://www.google.com/search?q=%s' % term.replace(' ', '+')
                r = requests.get(query, headers=user_agent, proxies=proxy, timeout=4)
                if r.status_code == 503:
                    print(x, "BAD Proxy: %s (%s)" % (ip, term))
                    bad_proxies.append(ip)
                    bad_blocks.add(block)
                else:
                    print(x, "Good Proxy: %s (%s)" % (ip, term))
                    good_proxies.append(ip)
                    good_blocks.add(block)
            except:
                print(x, "Unreachable Proxy:", ip)
                unreachable.append(ip)
    total_blocks = len(good_blocks) + len(bad_blocks)
    print()
    print("Out of %s proxies checked, we found %s good (not returning 503 codes)." % (x+1, len(good_proxies)))
    print("Out of %s C blocks in proxies, we found %s good and %s bad." % (total_blocks, len(good_blocks), len(bad_blocks)))
    with open('goodproxies.txt', 'w') as out:
        for proxy in good_proxies:
            out.write(proxy + '\n')
    print('goodproxies.txt updated.')
    print("The bad blocks are: ", bad_blocks)
    with open('badproxies.txt', 'w') as out:
        for proxy in bad_blocks:
            out.write(proxy + '\n')

if __name__ == '__main__':
    Main()

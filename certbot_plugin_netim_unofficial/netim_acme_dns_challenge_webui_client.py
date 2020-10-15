import argparse
from lxml import html
import requests

def init_session():
    return requests.Session()

def login(sess, login, pwd):
    page = sess.post('https://www.netim.com/direct/', data = {'LOGIN':login, 'PWD':pwd, 'LANG':'EN', 'connect':'1'})
    tree = html.fromstring(page.content)
    return page.status_code==200 and tree.xpath('//form[@id="LOGOUT"]/table/tr[1]/td[2]/b/text()')[0]==login

def logout(sess):
    page = sess.post('https://www.netim.com/direct/', data = {'deconnect':''})
    return page.status_code==200

def create_dns_challenge(sess, domain, challengeval, block=True):
    page = sess.post('https://www.netim.com/direct/ajax/controller/E44.php', data = {'TYPE':'TXT',
                                                                                     'A_HOST':'',
                                                                                     'A_IP1':'',
                                                                                     'A_IP2':'',
                                                                                     'A_IP3':'',
                                                                                     'A_IP4':'',
                                                                                     'submit_A':'0',
                                                                                     'AAAA_HOST':'',
                                                                                     'AAAA_IP':'',
                                                                                     'submit_AAAA':'0',
                                                                                     'NS_HOST':'',
                                                                                     'NS':'',
                                                                                     'submit_NS':'0',
                                                                                     'PTR_IP1':'',
                                                                                     'PTR_IP2':'',
                                                                                     'PTR_IP3':'',
                                                                                     'PTR_IP4':'',
                                                                                     'PRT_HOST':'',
                                                                                     'submit_PTR':'1',
                                                                                     'SRV_SERVICE':'',
                                                                                     'SRV_PROTOCOL':'tcp',
                                                                                     'SRV_TTL':'',
                                                                                     'SRV_PRIORITY':'50',
                                                                                     'SRV_WEIGHT':'',
                                                                                     'SRV_PORT':'',
                                                                                     'SRV_TARGET':'',
                                                                                     'SRV_HOST':'',
                                                                                     'submit_SRV':'0',
                                                                                     'TXT_HOST':'_acme-challenge',
                                                                                     'TXT':challengeval,
                                                                                     'submit_TXT':'1',
                                                                                     'MX_HOST':'',
                                                                                     'MX':'',
                                                                                     'MX_PRIORITY':'50',
                                                                                     'submit_MX':'0',
                                                                                     'CNAME_HOST':'',
                                                                                     'CNAME':'',
                                                                                     'submit_CNAME':'0',
                                                                                     '':'',
                                                                                     'domaine':domain,
                                                                                     'submitAddDns':'1'})
    return page.status_code==200 and str(page.content).find('STATUS_OPE=Done')!=-1

def remove_dns_challenge(sess, domain):
    page = sess.get('https://netim.com/direct/ajax/form/service/E10_dns_avance.php?domaine='+domain)
    tree = html.fromstring(page.content)
    entry_count = len(tree.xpath('//form[@id="DEL_DNS"]/table/tr'))
    assert entry_count >= 0
    for i in range(1,entry_count+1):
        if str(tree.xpath('//form[@id="DEL_DNS"]/table/tr['+str(i)+']/td[1]/text()')).find('_acme-challenge.'+domain)!=-1 and str(tree.xpath('//form[@id="DEL_DNS"]/table/tr['+str(i)+']/td[2]/text()')[0]).find('TXT')!=-1:
            assert str(tree.xpath('//form[@id="DEL_DNS"]/table/tr['+str(i)+']/td[2]/text()')[0]).find('TXT')!=-1
            checkbox_name = tree.xpath('//form[@id="DEL_DNS"]/table/tr['+str(i)+']/td[4]/input')[0].attrib['name']
            page = sess.post('https://www.netim.com/direct/ajax/controller/E10_domain.php', data = {'':'',
                                                                                                    'SUBMIT_DEL':'1',
                                                                                                    'domaine':domain,
                                                                                                    'submitDelDnsAvance':'1',
                                                                                                    checkbox_name:'1'})
            assert page.status_code==200

    return True         # TODO: less assertions more return status

def main():
    parser = argparse.ArgumentParser(description='Create LetsEncrypt DNS challenge for domains registered with netim.com')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-createchallenge', help='perform ACME challenge dns entry creation',action='store_true')
    group.add_argument('-removechallenge', help='perform ACME challenge dns entry removal',action='store_true')
    parser.add_argument('login', type=str, help='Account handle')
    parser.add_argument('password', type=str, help='Password')
    parser.add_argument('domain', type=str, help='Domain name')
    parser.add_argument('-challengevalue', type=str, default=None, help='ACME challenge value')
    args = parser.parse_args()

    sess = init_session()
    assert login(sess=sess, login=args.login, pwd=args.password)
    if args.createchallenge:
        assert args.challengevalue!=None, 'createchallenge requires challengevalue'
        assert create_dns_challenge(sess=sess, domain=args.domain, challengeval=args.challengevalue)
    elif args.removechallenge:
        assert remove_dns_challenge(sess=sess, domain='oeljeklaus.eu')
    assert logout(sess=sess)

    print('done')

if __name__ == "__main__":
    main()
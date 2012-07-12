PRODUCT_TYPES = ['pro', 'home']
LICENSE_TYPES = ['retail', 'oem', 'vlk']

LTYPE = dict(vlk='vol', oem='oem', retail='fpp')
PTYPE = dict(pro='p', home='h')



def iso_basename(product, license, language='en'):
    lic = LTYPE[license]
    prod = PTYPE[product]
    return 'wx%s%s_%s.iso' % (prod, lic, language)

if __name__ == '__main__':
    for p in PRODUCT_TYPES:
        for l in LICENSE_TYPES:
            print iso_basename(p, l)
            

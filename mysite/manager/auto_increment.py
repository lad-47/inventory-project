from home.models import Asset

def generateAssetTag():
    loop = True
    tag = 0
    while(loop):
        tag+=1
        try:
            Asset.objects.get(asset_tag=tag)
        except Asset.DoesNotExist:
            loop=False
    return tag
            
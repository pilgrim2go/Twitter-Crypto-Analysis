from PIL import Image

"""Add Logo To Bottom-Right Of Image"""
def add_logo(mfname, lfname, outfname):

    mimage = Image.open(mfname)
    limage = Image.open(lfname)

    # resize logo
    wsize = int(min(mimage.size[0], mimage.size[1]) * 0.24)
    wpercent = (wsize / float(limage.size[0]))
    hsize = int((float(limage.size[1]) * float(wpercent)))

    simage = limage.resize((wsize, hsize))
    mbox = mimage.getbbox()
    sbox = simage.getbbox()

    # right bottom corner
    box = (mbox[2] - sbox[2], mbox[3] - sbox[3])
    mimage.paste(simage, box)
    mimage.save(outfname)

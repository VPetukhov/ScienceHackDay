from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .utils import read_mesh, print_mesh, read_mask, displace_mask_vertices
import zipfile
import datetime

## SNPs from the paper below

snps = """
POLR1D	POLR1Da	rs507217	CA
CTNND2	CTNND2a	rs2277054	GA
SEMA3E	SEMA3E	rs2709922	GA
SLC35D1	SLC35D1	rs1074265	TA
FGFR1	FGFR1a	rs13267109	GA
WNT3	WNT3	rs199501	GA
LRP6	LRP6b	rs2724626	AC
SATB2	SATB2b	rs1357582	GA
EVC2	EVC2	rs10001971	AG
RAI1	RAI1d	rs4925108	AG
ADAMTS2	ADAMTS2	rs3822601	AG
ASPH	ASPH	rs4738909	CA
DNMT3B	DNMT3Bb	rs2424905	GA
RELN	RELNa	rs471360	AG
UFD1L	UFD1L	rs2073730	GC
SATB2	SATB2d	rs6759018	GA
SATB2	SATB2c	rs4530349	AG
ROR2	ROR2a	rs7029814	GA
SATB2	SATB2e	rs4673339	GA
FGFR2	FGFR2	rs2278202	GA
FBN1	FBN1b	rs6493315	GA
DNMT3B	DNMT3Bc	rs2424928	GA
GDF5	GDF5	rs143384	GA
COL11A1	COL11A1a	rs11164669	GA
""".strip()
snps = [row.split('\t') for row in snps.splitlines()]
snps = dict((row[2], row) for row in snps)

## SNPs from the paper above

# Be aware: ugly code below
@csrf_exempt
def index(request):
    if request.method != 'POST':
        return render(request, 'index.html', {})
    else:
        # Extract person's SNPs from the uploaded file
        dirname = request.FILES['23andme']
        d = zipfile.ZipFile(dirname)  # zipped dir (with single file)
        filename = d.namelist()[0]
        f = d.open(filename)  # zipped file
        personal_snps = {}
        sex = 'female'
        for row in f:
            row = row.decode('utf-8').strip().split('\t')
            if len(row) < 4:
                continue
            rsid, chromosome, position, genotype = row
            if chromosome == 'Y':
                sex = 'male'
            # use only rs-ID from the paper's snps
            if rsid in snps:
                name = snps[rsid][1]
                paper = snps[rsid][3]
                person = row[3]
                # make person similar to paper if they match
                if (person[1] == paper[0]) or (person[0] == paper[1]):
                    person = person[::-1]
                personal_snps[name] = (paper, person)

        vertices, faces, vert_normals = read_mesh('faceapp/static/faceapp/models/baseface.obj')

        if sex == 'male':
            mask = read_mask('faceapp/static/faceapp/models/Displace/Sex.txt')
            displace_mask_vertices(mask, vertices, 0.05)

        for snp, value in personal_snps.items():
            if value[0] == value[1]:
                mask = read_mask('faceapp/static/faceapp/models/Displace/{}.txt'.format(snp))
                displace_mask_vertices(mask, vertices, 0.05)
                # TODO: apply heatmap from snp.txt or something like that
                print('Applying heatmap for {}...'.format(snp))

        now = int(datetime.datetime.now().timestamp())
        result_url = '/static/faceapp/models/face-{}.obj'.format(now)
        result_path = 'faceapp' + result_url
        print_mesh(vertices, faces, vert_normals, result_path)

        # TODO: Use personal_snps for face rendering

        return render(request, 'face.html', {
            'filename': filename,
            'personal_snps': personal_snps,
            'sex': sex,
            'facemodel_url': result_url,
            'facemodel_absolute_url': 'http://ec2-52-30-55-26.eu-west-1.compute.amazonaws.com' + result_url  # the face will work when deployed only
        })

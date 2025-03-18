from django.shortcuts import render, redirect
from django.http import JsonResponse
import requests
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import base64
from .models import *
import re
from datetime import datetime
import json
import uuid
import pysolr

url_base_solr = 'http://cosmos-validacion-integridad-sipecam.conabio.gob.mx:8985/solr/'
url_base_img = 'http://cosmos-validacion-integridad-sipecam.conabio.gob.mx:777/'
#url_user_management = 'http://sipecamdata.conabio.gob.mx:888'
url_user_management = 'http://127.0.0.1:5000'
image_width = 300
image_height = 300


def login(request):
    context = {}
    response = render(request, "login.html", context)
    if request.method=='POST':
        url = url_user_management + '/login'
        res = requests.post(url, 
            json={
                'email': request.POST['email'], 
                'password': request.POST['password']
            },
            headers={
                'content-type': 'application/json'
            }
        )
        id_user = None
        bearer_token = None
        if res.status_code == 200:
            body_res = res.json()
            print(body_res)
            id_user = body_res['id_user']
            bearer_token = body_res['bearer_token']
            if id_user == None or bearer_token == None:
                context['warn'] = 'Usuario inválido'
                context['error'] = True
                response = render(request, "login.html", context)
            if id_user != None and bearer_token != None:
                response.set_cookie(key='logged', value=True)
                response.set_cookie(key='id_user', value=id_user)
                response.set_cookie(key='bearer_token', value=bearer_token)
                request.session['id_user'] = id_user
                redirect('cow/0/')
                print('Logueado')
    return response


def index(request, page):
    species = ParametrizedSpecies.objects.all()
    context = {'page': page, 'prev': page-1, 'next': page+1, 'species': species}
    return render(request, "index.html", context)


def images(request, page):
    last_fecha_foto = '2000-01-01T00:00:00Z'
    last_fecha_foto_qs = Photo.objects.filter(checked=True).order_by('-fecha_foto')
    if last_fecha_foto_qs.count() > 0:
        last_fecha_foto = last_fecha_foto_qs[0].fecha_foto.strftime('%Y-%m-%dT%H:%M:%SZ')
    images_res = {'images': []}
    url = url_base_solr + 'sipecam/select?wt=json&rows=20&start={0}&q=new_deliveries:true%20AND%20fecha_foto:[{1} TO *]&fq={{!join%20from=ftrampa_id%20to=id%20fromIndex=anotaciones}}modelo_id:megadetector_v5a%20AND%20probabilidad_modelo:[40%20TO%20100]%20AND%20etiqueta:animal%20AND%20coleccion:sipecam&sort=labeled%20asc,%20fecha_foto%20asc'.format(20*page, last_fecha_foto)
    res = requests.get(url, headers={'content-type': 'application/json'}).json()
    print(res)
    for img in res['response']['docs']:
        ## Getting annotations
        url = url_base_solr + 'anotaciones/select?wt=json&q=ftrampa_id:{0}%20AND%20coleccion:%22sipecam%22%20'.format(img['id'])
        res = requests.get(url, headers={'content-type': 'application/json'}).json()
        ## Checking if detection already were downloaded
        photo_record = None
        try:
            photo_record = Photo.objects.get(ftrampa_id=img['id'])
        except Exception as e:
            print('Error photo ' + str(e))
            ## Creating new photo record
            photo_record = Photo()
            photo_record.ftrampa_id = img['id']
            photo_record.ruta = img['ruta']
            photo_record.fecha_foto = img['fecha_foto']
            photo_record.save()
            ## Downloading image
            res_img = requests.get(url_base_img + photo_record.ruta)
            if res_img.status_code == 200:
                photo_image = Image.open(BytesIO(res_img.content))
                ## Cropping image
                for ann in res['response']['docs']:
                    try:
                        annotation = Annotation.objects.get(annotation_id=ann['id'])
                    except Exception as e:
                        print('Error annotation ' + str(e))
                        ## Creating annotation record
                        cropped_image_filename = f"img-{ann['id']}.jpg"
                        image_width, image_height = photo_image.size
                        p1_x, p1_y = int(image_width*ann['rect_x']), int(image_height*ann['rect_y'])
                        p2_x, p2_y = p1_x + int(image_width*ann['rect_width']), p1_y + int(image_height*ann['rect_height'])
                        bbox = (p1_x, p1_y, p2_x, p2_y)
                        annotation_record = Annotation()
                        annotation_record.ftrampa_id = img['id']
                        annotation_record.annotation_id = ann['id']
                        annotation_record.p1_x = p1_x
                        annotation_record.p1_y = p1_y
                        annotation_record.p2_x = p2_x
                        annotation_record.p2_y = p2_y
                        ## Saving cropped images
                        cropped_image = photo_image.crop(bbox)
                        buffer = BytesIO()
                        cropped_image.save(buffer, format='JPEG')
                        base64_image = base64.b64encode(buffer.getvalue()).decode()
                        imagen_data = re.sub('^data:image/.+;base64,', '', base64_image)
                        imagen_bytes = base64.b64decode(imagen_data)
                        image_file = ContentFile(imagen_bytes, cropped_image_filename)
                        file_path = default_storage.save('cropped_images/' + cropped_image_filename, image_file)
                        annotation_record.path = file_path
                        annotation_record.save()
        annotations = Annotation.objects.filter(ftrampa_id=img['id'])
        for ann in annotations:
            images_res['images'].append({'path': ann.path, 'id': ann.id, 'indexed': ann.indexed})
    return JsonResponse(images_res)


def send_annotations(request):
    solr_anotaciones = pysolr.Solr(f'{url_base_solr}/anotaciones', always_commit=True)
    data = {'indexed_images': []}
    body = json.loads(request.body)
    selected_images = body['selected_images']
    sp_id = body['sp_id']
    #print(request.session['id_user'])
    sp = ParametrizedSpecies.objects.get(id=sp_id)
    for si in selected_images:
        try:
            ann_obj = Annotation.objects.get(id=si)
            ann_bod = {
                "taxa_id": sp.taxa_id,
                "numero_individuos": "1",
                "ftrampa_id": ann_obj.ftrampa_id,
                "etiqueta_str": sp.species,
                "clase": sp.clase,
                "especie": sp.species,
                "etiqueta": sp.species,
                "tipo_anotacion":"especimen",
                "coleccion": "sipecam",
                "genero": sp.genero,
                "rect_y": ann_obj.p1_y,
                "orden": sp.orden,
                "rect_height": ann_obj.p2_y-ann_obj.p1_y,
                "rect_x": ann_obj.p1_x,
                "id": str(uuid.uuid4()),
                "rect_width": ann_obj.p2_x-ann_obj.p1_x,
                "especie_str": sp.species,
                "reino": sp.reino,
                "phylum": sp.phylum,
                "nivel_anotador":"usuario",
                "fecha_anotacion":datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "certeza":"alta",
                "ultima_modificacion":datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "familia": sp.familia,
                "anotador_id": request.session['id_user'],
            }
            print(ann_bod)
            solr_anotaciones.add([ann_bod])
            data['indexed_images'].append(si)
            ann_obj.indexed = True
            ann_obj.save()
        except Exception as e:
            print(str(e))
    return JsonResponse(data)


#def annotation(request, ftrampa_id):
#    url = url_base_solr + 'anotaciones/select?wt=json&q=ftrampa_id:{0}%20AND%20coleccion:%22sipecam%22%20AND%20nivel_anotador:algoritmo'.format(ftrampa_id)
#    res = requests.get(url, headers={'content-type': 'application/json'}).json()
#    return JsonResponse(res)

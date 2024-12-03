import boto3
from flask import request, jsonify, Blueprint

from app.database.db_mysql import db
from app.models import Etiqueta, Meme
from app.imagga import get_image_tags  # Importamos la función para obtener las etiquetas de Imagga

routes = Blueprint('routes', __name__)

# Configuración del cliente S3
S3_BUCKET = "meme-storagee"  # Cambia por el nombre de tu bucket
S3_REGION = "us-east-2"
s3_client = boto3.client('s3', region_name=S3_REGION)

@routes.route('/')
def home():
    return "<h1>¡Bienvenido a Cloud MemeDB!</h1>"

@routes.route('/upload', methods=['POST'])
def upload_meme():
    try:
        # Verifica si el archivo está en la solicitud
        if 'file' not in request.files:
            return jsonify({"error": "No se encontró el campo 'file' en la solicitud"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No se seleccionó ningún archivo"}), 400

        descripcion = request.form.get('descripcion', '')
        usuario = request.form.get('usuario', '')
        etiquetas = request.form.get('etiquetas', '')

        if not descripcion or not usuario or not etiquetas:
            return jsonify({"error": "Faltan campos requeridos"}), 400

        # Subir el archivo a S3
        s3_client.upload_fileobj(
            file,
            S3_BUCKET,
            file.filename,
            ExtraArgs={"ContentType": file.content_type}
        )

        # Crear la URL del archivo subido
        ruta_s3 = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{file.filename}"

        # Analizar la imagen con Imagga para obtener etiquetas
        tags_response = get_image_tags(file)  # Usamos la función que conecta con la API de Imagga
        if 'error' in tags_response:
            return jsonify({"error": "Error al analizar la imagen", "details": tags_response['error']}), 500

        # Extraer las etiquetas generadas por Imagga
        tags = [tag['tag']['en'] for tag in tags_response['result']['tags'] if tag['confidence'] > 50]

        # Guardar el meme en la base de datos
        meme = Meme(descripcion=descripcion, ruta=ruta_s3, usuario=usuario)
        db.session.add(meme)
        db.session.commit()

        # Guardar las etiquetas en la base de datos
        for tag in tags:
            if not Etiqueta.query.filter_by(etiqueta=tag, meme_id=meme.id).first():
                nueva_etiqueta = Etiqueta(meme_id=meme.id, etiqueta=tag, confianza=0.75)  # Ajustar confianza
                db.session.add(nueva_etiqueta)

        db.session.commit()

        return jsonify({"message": "Meme cargado exitosamente", "ruta": ruta_s3, "tags": tags}), 200

    except Exception as e:
        # Captura y muestra el error
        print(f"Error durante la carga o análisis de la imagen: {str(e)}")
        return jsonify({"error": "Error interno del servidor", "details": str(e)}), 500



@routes.route('/search', methods=['GET'])
def search_meme():
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify({"error": "Se necesita un término de búsqueda"}), 400

    memes = Meme.query.filter(Meme.descripcion.ilike(f"%{query}%")).all()
    resultados = [{"descripcion": meme.descripcion, "usuario": meme.usuario} for meme in memes]

    return jsonify(resultados), 200

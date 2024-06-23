from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId
from models import mongo

kepala_bagian_bp = Blueprint(
    "api/kepala_bagian", __name__, url_prefix="/api/kepala_bagian"
)


@kepala_bagian_bp.route("/ajukan", methods=["GET"])
def ajukan():
    # Retrieve all items that are verified
    verified_items = list(mongo.db.sub_bag.find({"is_verif": True}))
    for item in verified_items:
        item["_id"] = str(item["_id"])

    # Insert each verified item into the kepala_bagian collection
    new_documents = []
    for sub_bag in verified_items:
        ajukan_id = mongo.db.kepala_bagian.insert_one(
            {
                "id_sub_bag": sub_bag["_id"],
                "tanggal_pengusulan": sub_bag["tanggal_penerimaan"],
                "tanggal_penerimaan": None,
                "nama_barang": sub_bag["nama_barang"],
                "volume": sub_bag["volume"],
                "merek": sub_bag["merek"],
                "ruangan": sub_bag["ruangan"],
                "jumlah_diterima": 0,
                "is_verif": False,
                "status": "Process",
            }
        ).inserted_id

        # Retrieve the newly inserted document
        new_ajukan = mongo.db.kepala_bagian.find_one({"_id": ajukan_id})
        new_ajukan["_id"] = str(new_ajukan["_id"])
        new_documents.append(new_ajukan)

    return jsonify({"kepala_bagian": new_documents}), 201


# @kepala_bagian_bp.route("/ajukan", methods=["GET"])
# def get_all_ajukan():

#     ajukan_items = list(mongo.db.kepala_bagian.find())
#     for item in ajukan_items:
#         item["_id"] = str(item["_id"])
#     return jsonify({"kepala_bagian": ajukan_items})


@kepala_bagian_bp.route("/ajukan/<ajukan_id>", methods=["GET"])
def get_ajukan(ajukan_id):
    ajukan_item = mongo.db.kepala_bagian.find_one({"_id": ObjectId(ajukan_id)})
    if not ajukan_item:
        return jsonify({"message": "Ajukan item not found"}), 404
    ajukan_item["_id"] = str(ajukan_item["_id"])
    return jsonify(ajukan_item)


@kepala_bagian_bp.route("/verifikasi", methods=["POST"])
def verifikasi():
    data = request.get_json()
    ajukan_id = data.get("id_ajukan")
    jumlah_diterima = data.get("jumlah_diterima")
    tanggal_penerimaan = data.get("tanggal_penerimaan")
    alasan = data.get("alasan")
    status = data.get("status")

    if not ajukan_id or jumlah_diterima is None or not tanggal_penerimaan:
        return jsonify({"message": "Missing required fields"}), 400

    ajukan = mongo.db.kepala_bagian.find_one({"_id": ObjectId(ajukan_id)})
    if not ajukan:
        return jsonify({"message": "Invalid id_ajukan"}), 400

    volume = int(ajukan["volume"])

    if int(jumlah_diterima) > volume:
        return (
            jsonify({"message": "Jumlah diterima cannot be greater than volume"}),
            400,
        )

    is_verif = jumlah_diterima == volume

    result = mongo.db.kepala_bagian.update_one(
        {"_id": ObjectId(ajukan_id)},
        {
            "$set": {
                "jumlah_diterima": jumlah_diterima,
                "is_verif": is_verif,
                "tanggal_penerimaan": tanggal_penerimaan,
                "status": status,
                "alasan": alasan,
            }
        },
    )

    if result.modified_count == 1:
        return jsonify({"message": "Verification completed successfully"})
    else:
        return jsonify({"message": "Verification failed"}), 500


@kepala_bagian_bp.route("/verifikasi_true", methods=["GET"])
def get_verified_ajukan():
    verified_items = list(mongo.db.kepala_bagian.find({"is_verif": True}))
    for item in verified_items:
        item["_id"] = str(item["_id"])
    return jsonify({"verified_kepala_bagian": verified_items})


@kepala_bagian_bp.route("/verifikasi_false", methods=["GET"])
def get_unverified_ajukan():
    unverified_items = list(mongo.db.kepala_bagian.find({"is_verif": False}))
    for item in unverified_items:
        item["_id"] = str(item["_id"])
    return jsonify({"unverified_kepala_bagian": unverified_items})

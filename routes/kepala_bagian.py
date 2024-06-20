from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId
from models import mongo

kepala_bagian_bp = Blueprint(
    "api/kepala_bagian", __name__, url_prefix="/api/kepala_bagian"
)


@kepala_bagian_bp.route("/ajukan", methods=["POST"])
def ajukan():
    data = request.get_json()
    id_sub_bag = data.get("id_sub_bag")

    if not id_sub_bag:
        return jsonify({"message": "Missing required field id_sub_bag"}), 400

    sub_bag = mongo.db.sub_bag.find_one({"_id": ObjectId(id_sub_bag), "is_verif": True})
    if not sub_bag:
        return jsonify({"message": "Invalid or unverified id_sub_bag"}), 400

    ajukan_id = mongo.db.kepala_bagian.insert_one(
        {
            "id_sub_bag": id_sub_bag,
            "tanggal_pengusulan": sub_bag["tanggal_penerimaan"],
            "tanggal_penerimaan": None,
            "nama_barang": sub_bag["nama_barang"],
            "volume": sub_bag["volume"],
            "merek": sub_bag["merek"],
            "ruangan": sub_bag["ruangan"],
            "jumlah_diterima": 0,
            "is_verif": False,
        }
    ).inserted_id

    new_ajukan = mongo.db.kepala_bagian.find_one({"_id": ajukan_id})
    new_ajukan["_id"] = str(new_ajukan["_id"])

    return jsonify(new_ajukan), 201


@kepala_bagian_bp.route("/ajukan", methods=["GET"])
def get_all_ajukan():
    ajukan_items = list(mongo.db.kepala_bagian.find())
    for item in ajukan_items:
        item["_id"] = str(item["_id"])
    return jsonify({"kepala_bagian": ajukan_items})


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

    if not ajukan_id or jumlah_diterima is None or not tanggal_penerimaan:
        return jsonify({"message": "Missing required fields"}), 400

    ajukan = mongo.db.kepala_bagian.find_one({"_id": ObjectId(ajukan_id)})
    if not ajukan:
        return jsonify({"message": "Invalid id_ajukan"}), 400

    volume = int(ajukan["volume"])

    if jumlah_diterima > volume:
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

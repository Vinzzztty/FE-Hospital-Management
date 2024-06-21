from flask import Blueprint, request, jsonify
from bson import ObjectId
from models import mongo

staff_gudang_bp = Blueprint(
    "api/staff_gudang", __name__, url_prefix="/api/staff_gudang"
)


@staff_gudang_bp.route("/ajukan", methods=["POST"])
def ajukan():
    data = request.get_json()
    id_pengajuan_barang = data.get("id_pengajuan_barang")

    if not id_pengajuan_barang:
        return jsonify({"message": "Missing required fields"}), 400

    # Fetch the pengajuan_barang document
    pengajuan_barang = mongo.db.pengajuan_barang.find_one(
        {"_id": ObjectId(id_pengajuan_barang)}
    )

    if not pengajuan_barang:
        return jsonify({"message": "Pengajuan Barang not found"}), 404

    # Extract details from the referenced document
    tanggal_pengajuan = pengajuan_barang.get("tanggal_pengajuan")
    tanggal_penerimaan = pengajuan_barang.get("tanggal_penerimaan")
    nama_barang = pengajuan_barang.get("nama_barang")
    jumlah = pengajuan_barang.get("jumlah")
    ruangan = pengajuan_barang.get("ruangan")

    staff_gudang_id = mongo.db.staff_gudang.insert_one(
        {
            "id_pengajuan_barang": id_pengajuan_barang,
            "tanggal_pengajuan": tanggal_pengajuan,
            "tanggal_penerimaan": tanggal_penerimaan,
            "nama_barang": nama_barang,
            "jumlah": jumlah,
            "ruangan": ruangan,
            "jumlah_diterima": 0,  # Default value
            "is_verif": False,  # Set is_verif to False by default
        }
    ).inserted_id

    new_sub_bag = mongo.db.staff_gudang.find_one({"_id": staff_gudang_id})
    new_sub_bag["_id"] = str(new_sub_bag["_id"])  # Convert ObjectId to string
    new_sub_bag["id_pengajuan_barang"] = str(
        new_sub_bag["id_pengajuan_barang"]
    )  # Ensure reference ID is also a string

    return jsonify(new_sub_bag), 201


@staff_gudang_bp.route("/ajukan", methods=["GET"])
def get_all_ajukan():
    staff_gudang_items = list(mongo.db.staff_gudang.find())

    for item in staff_gudang_items:
        item["_id"] = str(item["_id"])
        item["id_pengajuan_barang"] = str(item["id_pengajuan_barang"])

    return jsonify({"staff_gudang": staff_gudang_items}), 200


@staff_gudang_bp.route("/ajukan/<ajukan_id>", methods=["GET"])
def get_ajukan_detail(ajukan_id):
    staff_gudang_item = mongo.db.staff_gudang.find_one({"_id": ObjectId(ajukan_id)})

    if not staff_gudang_item:
        return jsonify({"message": "Ajukan not found"}), 404

    staff_gudang_item["_id"] = str(staff_gudang_item["_id"])
    staff_gudang_item["id_pengajuan_barang"] = str(
        staff_gudang_item["id_pengajuan_barang"]
    )

    return jsonify(staff_gudang_item), 200


@staff_gudang_bp.route("/verifikasi", methods=["POST"])
def verifikasi():
    data = request.get_json()
    ajukan_id = data.get("id_ajukan")
    jumlah_diterima = data.get("jumlah_diterima")

    if not ajukan_id or jumlah_diterima is None:
        return jsonify({"message": "Missing required fields"}), 400

    ajukan = mongo.db.staff_gudang.find_one({"_id": ObjectId(ajukan_id)})
    if not ajukan:
        return jsonify({"message": "Invalid id_ajukan"}), 400

    jumlah = int(ajukan["jumlah"])

    if jumlah_diterima > jumlah:
        return (
            jsonify({"message": "Jumlah diterima cannot be greater than jumlah awal"}),
            400,
        )

    is_verif = jumlah_diterima == jumlah

    result = mongo.db.staff_gudang.update_one(
        {"_id": ObjectId(ajukan_id)},
        {"$set": {"jumlah_diterima": jumlah_diterima, "is_verif": is_verif}},
    )

    if result.modified_count == 1:
        return jsonify({"message": "Verification completed successfully"})
    else:
        return jsonify({"message": "Verification failed"}), 500


@staff_gudang_bp.route("/verifikasi_true", methods=["GET"])
def get_verified_ajukan():
    verified_items = list(mongo.db.staff_gudang.find({"is_verif": True}))
    for item in verified_items:
        item["_id"] = str(item["_id"])
    return jsonify({"verified_staff_gudang": verified_items})


@staff_gudang_bp.route("/verifikasi_false", methods=["GET"])
def get_unverified_ajukan():
    unverified_items = list(mongo.db.staff_gudang.find({"is_verif": False}))
    for item in unverified_items:
        item["_id"] = str(item["_id"])
    return jsonify({"unverified_staff_gudang": unverified_items})

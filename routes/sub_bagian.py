from flask import Blueprint, request, jsonify
from bson import ObjectId
from models import mongo

sub_bagian_bp = Blueprint("api/sub_bagian", __name__, url_prefix="/api/sub_bagian")


# POST route to create a new sub_bag item (ajukan)
@sub_bagian_bp.route("/ajukan", methods=["POST"])
def ajukan():
    data = request.get_json()
    id_pengusulan_barang = data.get("id_pengusulan_barang")

    if not id_pengusulan_barang:
        return jsonify({"message": "Missing required fields"}), 400

    # Fetch the pengusulan_barang document
    pengusulan_barang = mongo.db.pengusulan_barang.find_one(
        {"_id": ObjectId(id_pengusulan_barang)}
    )

    if not pengusulan_barang:
        return jsonify({"message": "Referenced pengusulan_barang not found"}), 404

    # Extract details from the referenced document
    tanggal_pengusulan = pengusulan_barang.get("tanggal_pengusulan")
    tanggal_penerimaan = pengusulan_barang.get("tanggal_penerimaan")
    nama_barang = pengusulan_barang.get("nama_barang")
    volume = pengusulan_barang.get("volume")
    merek = pengusulan_barang.get("merek")
    ruangan = pengusulan_barang.get("ruangan")

    sub_bag_id = mongo.db.sub_bag.insert_one(
        {
            "id_pengusulan_barang": id_pengusulan_barang,
            "tanggal_pengusulan": tanggal_pengusulan,
            "tanggal_penerimaan": tanggal_penerimaan,
            "nama_barang": nama_barang,
            "volume": volume,
            "merek": merek,
            "ruangan": ruangan,
            "jumlah_diterima": 0,  # Default value
            "is_verif": False,  # Set is_verif to False by default
        }
    ).inserted_id

    new_sub_bag = mongo.db.sub_bag.find_one({"_id": sub_bag_id})
    new_sub_bag["_id"] = str(new_sub_bag["_id"])  # Convert ObjectId to string
    new_sub_bag["id_pengusulan_barang"] = str(
        new_sub_bag["id_pengusulan_barang"]
    )  # Ensure reference ID is also a string

    return jsonify(new_sub_bag), 201


# GET route to retrieve all sub_bag items
@sub_bagian_bp.route("/ajukan", methods=["GET"])
def get_all_ajukan():
    sub_bag_items = list(mongo.db.sub_bag.find())

    # Convert ObjectId to string for JSON serialization
    for item in sub_bag_items:
        item["_id"] = str(item["_id"])
        item["id_pengusulan_barang"] = str(item["id_pengusulan_barang"])

    return jsonify({"sub_bag": sub_bag_items}), 200


# GET route to retrieve a specific sub_bag item by ID
@sub_bagian_bp.route("/ajukan/<ajukan_id>", methods=["GET"])
def get_ajukan_detail(ajukan_id):
    sub_bag_item = mongo.db.sub_bag.find_one({"_id": ObjectId(ajukan_id)})

    if not sub_bag_item:
        return jsonify({"message": "Ajukan not found"}), 404

    sub_bag_item["_id"] = str(sub_bag_item["_id"])  # Convert ObjectId to string
    sub_bag_item["id_pengusulan_barang"] = str(sub_bag_item["id_pengusulan_barang"])

    return jsonify(sub_bag_item), 200


# POST route for verification
@sub_bagian_bp.route("/verifikasi", methods=["POST"])
def verifikasi():
    data = request.get_json()
    ajukan_id = data.get("id_ajukan")
    jumlah_diterima = data.get("jumlah_diterima")

    if not ajukan_id or jumlah_diterima is None:
        return jsonify({"message": "Missing required fields"}), 400

    ajukan = mongo.db.sub_bag.find_one({"_id": ObjectId(ajukan_id)})
    if not ajukan:
        return jsonify({"message": "Invalid id_ajukan"}), 400

    volume = int(ajukan["volume"])

    if jumlah_diterima > volume:
        return (
            jsonify({"message": "Jumlah diterima cannot be greater than volume"}),
            400,
        )

    is_verif = jumlah_diterima == volume

    result = mongo.db.sub_bag.update_one(
        {"_id": ObjectId(ajukan_id)},
        {"$set": {"jumlah_diterima": jumlah_diterima, "is_verif": is_verif}},
    )

    if result.modified_count == 1:
        return jsonify({"message": "Verification completed successfully"})
    else:
        return jsonify({"message": "Verification failed"}), 500


@sub_bagian_bp.route("/verifikasi_true", methods=["GET"])
def get_verified_ajukan():
    verified_items = list(mongo.db.sub_bag.find({"is_verif": True}))
    for item in verified_items:
        item["_id"] = str(item["_id"])
    return jsonify({"verified_sub_bag": verified_items})


@sub_bagian_bp.route("/verifikasi_false", methods=["GET"])
def get_unverified_ajukan():
    unverified_items = list(mongo.db.sub_bag.find({"is_verif": False}))
    for item in unverified_items:
        item["_id"] = str(item["_id"])
    return jsonify({"unverified_sub_bag": unverified_items})

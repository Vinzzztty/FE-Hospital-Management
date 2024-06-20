from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId
from models import mongo

staff_ruangan_bp = Blueprint(
    "api/staff_ruangan", __name__, url_prefix="/api/staff_ruangan"
)

ALLOWED_BARANG = ["Tisu", "HVS", "Sabun", "Hand Sanitizer"]


# GET route to retrieve all pengajuan items
@staff_ruangan_bp.route("/pengajuan_barang", methods=["GET"])
def get_pengajuan_barang():
    pengajuan_items = list(mongo.db.pengajuan_barang.find())

    # Convert ObjectId to string for JSON serialization
    for item in pengajuan_items:
        item["_id"] = str(item["_id"])

    return jsonify({"pengajuan_barang": pengajuan_items})


@staff_ruangan_bp.route("/pengajuan_barang", methods=["POST"])
def pengajuan_barang():
    data = request.get_json()
    role = data.get("role")
    nama_barang = data.get("nama_barang")
    tanggal_pengajuan = data.get("tanggal_pengajuan")
    tanggal_penerimaan = None
    jumlah = data.get("jumlah")
    ruangan = data.get("ruangan")
    is_verif = False

    if not all([role, tanggal_pengajuan, nama_barang, jumlah, ruangan]):
        return jsonify({"message": "Missing required fields"}), 400

    if nama_barang not in ALLOWED_BARANG:
        return (
            jsonify(
                {
                    "message": f"Invalid nama_barang. Allowed values are: {', '.join(ALLOWED_BARANG)}"
                }
            ),
            400,
        )

    pengajuan_id = mongo.db.pengajuan_barang.insert_one(
        {
            "role": role,
            "tanggal_pengajuan": tanggal_pengajuan,
            "tanggal_penerimaan": tanggal_penerimaan,
            "nama_barang": nama_barang,
            "jumlah": jumlah,
            "ruangan": ruangan,
            "is_verif": is_verif,
        }
    ).inserted_id

    new_pengajuan = mongo.db.pengajuan_barang.find_one({"_id": pengajuan_id})
    new_pengajuan["_id"] = str(new_pengajuan["_id"])  # Convert ObjectId to string
    return jsonify(new_pengajuan), 201


# PUT route to update a pengajuan item
@staff_ruangan_bp.route("/pengajuan_barang/<pengajuan_id>", methods=["PUT"])
def update_pengajuan_barang(pengajuan_id):
    data = request.get_json()
    updated_fields = {}

    # Check if nama_barang is provided and is valid
    if "nama_barang" in data and data["nama_barang"] in ALLOWED_BARANG:
        updated_fields["nama_barang"] = data["nama_barang"]

    # Check if jumlah is provided
    if "jumlah" in data:
        updated_fields["jumlah"] = data["jumlah"]

    # Check if tanggal_penerimaan is provided
    if "tanggal_penerimaan" in data:
        updated_fields["tanggal_penerimaan"] = data["tanggal_penerimaan"]

    # If no fields to update are provided
    if not updated_fields:
        return jsonify({"message": "No valid fields to update"}), 400

    result = mongo.db.pengajuan_barang.update_one(
        {"_id": ObjectId(pengajuan_id)}, {"$set": updated_fields}
    )

    if result.modified_count == 1:
        return jsonify({"message": "Pengajuan item updated successfully"})
    else:
        return jsonify({"message": "Pengajuan item not found"}), 404


# DELETE route to delete a pengajuan item
@staff_ruangan_bp.route("/pengajuan_barang/<pengajuan_id>", methods=["DELETE"])
def delete_pengajuan_barang(pengajuan_id):
    result = mongo.db.pengajuan_barang.delete_one({"_id": ObjectId(pengajuan_id)})
    if result.deleted_count == 1:
        return jsonify({"message": "Pengajuan item deleted successfully"})
    else:
        return jsonify({"message": "Pengajuan item not found"}), 404


# DELETE route to delete all pengajuan items
@staff_ruangan_bp.route("/pengajuan_barang", methods=["DELETE"])
def delete_all_pengajuan_barang():
    result = mongo.db.pengajuan_barang.delete_many(
        {}
    )  # Delete all documents in the collection

    if result.deleted_count > 0:
        return jsonify({"message": "All pengajuan items deleted successfully"})
    else:
        return jsonify({"message": "No pengajuan items found to delete"}), 404


# GET route to retrieve all pengajuan items
@staff_ruangan_bp.route("/pengusulan_barang", methods=["GET"])
def get_pengusulan_barang():
    pengusulan_items = list(mongo.db.pengusulan_barang.find())

    # Convert ObjectId to string for JSON serialization
    for item in pengusulan_items:
        item["_id"] = str(item["_id"])

    return jsonify({"pengusulan_barang": pengusulan_items})


@staff_ruangan_bp.route("/pengusulan_barang", methods=["POST"])
def pengusulan_barang():
    data = request.get_json()
    role = data.get("role")
    tanggal_penerimaan = data.get("tanggal_penerimaan")
    tanggal_pengusulan = data.get("tanggal_pengusulan")
    nama_barang = data.get("nama_barang")
    volume = data.get("volume")
    merek = data.get("merek")
    ruangan = data.get("ruangan")

    if not all([role, tanggal_pengusulan, nama_barang, volume, merek]):
        return jsonify({"message": "Missing required fields"}), 400

    pengusulan_id = mongo.db.pengusulan_barang.insert_one(
        {
            "role": role,
            "tanggal_pengusulan": tanggal_pengusulan,
            "tanggal_penerimaan": tanggal_penerimaan,
            "nama_barang": nama_barang,
            "volume": volume,
            "merek": merek,
            "ruangan": ruangan,
        }
    ).inserted_id

    new_pengusulan = mongo.db.pengusulan_barang.find_one({"_id": pengusulan_id})
    new_pengusulan["_id"] = str(new_pengusulan["_id"])  # Convert ObjectId to string
    return jsonify(new_pengusulan), 201


# PUT route to update a pengusulan item
@staff_ruangan_bp.route("/pengusulan_barang/<pengusulan_id>", methods=["PUT"])
def update_pengusulan_barang(pengusulan_id):
    data = request.get_json()
    updated_fields = {}

    # Check if nama_barang is provided and is valid
    if "nama_barang" in data:
        updated_fields["nama_barang"] = data["nama_barang"]

    # Check if volume is provided
    if "volume" in data:
        updated_fields["volume"] = data["volume"]

    # Check if volume is provided
    if "tanggal_penerimaan" in data:
        updated_fields["tanggal_penerimaan"] = data["tanggal_penerimaan"]

    # If no fields to update are provided
    if not updated_fields:
        return jsonify({"message": "No valid fields to update"}), 400

    result = mongo.db.pengusulan_barang.update_one(
        {"_id": ObjectId(pengusulan_id)}, {"$set": updated_fields}
    )

    if result.modified_count == 1:
        return jsonify({"message": "Pengusulan item updated successfully"})
    else:
        return jsonify({"message": "Pengusulan item not found"}), 404


# DELETE route to delete a pengusulan item
@staff_ruangan_bp.route("/pengusulan_barang/<pengusulan_id>", methods=["DELETE"])
def delete_pengusulan_barang(pengusulan_id):
    result = mongo.db.pengusulan_barang.delete_one({"_id": ObjectId(pengusulan_id)})
    if result.deleted_count == 1:
        return jsonify({"message": "Pengusulan item deleted successfully"})
    else:
        return jsonify({"message": "Pengusulan item not found"}), 404


# DELETE route to delete all pengusulan items
@staff_ruangan_bp.route("/pengusulan_barang", methods=["DELETE"])
def delete_all_pengusulan_barang():
    result = mongo.db.pengusulan_barang.delete_many(
        {}
    )  # Delete all documents in the collection

    if result.deleted_count > 0:
        return jsonify({"message": "All pengusulan items deleted successfully"})
    else:
        return jsonify({"message": "No pengusulan items found to delete"}), 404

from flask import Blueprint, jsonify, request
from bson.objectid import ObjectId
from models import mongo
from pymongo.errors import PyMongoError

transaksi_bp = Blueprint("api/transaksi", __name__, url_prefix="/api/transaksi")


@transaksi_bp.route("/", methods=["POST"])
def create_transaksi():
    try:
        transaction_data = request.json  # Assuming JSON data in the request body

        # Insert the transaction data into the 'transaksi' collection
        result = mongo.db.transaksi.insert_one(transaction_data)

        # Retrieve the inserted document to confirm success
        inserted_document = mongo.db.transaksi.find_one({"_id": result.inserted_id})

        if inserted_document:
            # Convert ObjectId to string for JSON serialization
            inserted_document["_id"] = str(inserted_document["_id"])
            return (
                jsonify(
                    {
                        "message": "Transaction created successfully",
                        "transaction": inserted_document,
                    }
                ),
                201,
            )
        else:
            return jsonify({"error": "Failed to retrieve inserted transaction"}), 500

    except PyMongoError as e:
        error_message = f"MongoDB error: {str(e)}"
        return jsonify({"error": error_message}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 400


def fetch_transaksi_data():
    all_transaksi = {
        "pengusulan": [],
        "pengajuan_barang": [],
    }

    try:
        # Fetch data from MongoDB collections for each role
        sub_bag_transaksi = list(mongo.db.sub_bag.find())
        kepala_bagian_transaksi = list(mongo.db.kepala_bagian.find())
        verifikasi_transaksi = list(mongo.db.verifikasi.find())
        staff_gudang = list(mongo.db.staff_gudang.find())

        # Create sets to track IDs for deletion
        delete_ids = set()

        # Process verifikasi_transaksi first to identify deletions
        for item in verifikasi_transaksi:
            item["_id"] = str(item["_id"])
            item["role"] = "Verifikasi"

            if item["status"] == "Process":
                delete_ids.add(item["_id"])
            elif item.get("is_verif", False):
                item["status"] = item["status"]
            elif item["status"] == "Success":
                item["status"] = "Success"
            elif item["status"] == "Decline":
                item["status"] = "Decline"
            else:
                item["status"] = "Unknown"
                all_transaksi["pengusulan"].append(item)

        # Process kepala_bagian_transaksi
        kepala_bagian_to_add = []
        for item in kepala_bagian_transaksi:
            item["_id"] = str(item["_id"])
            item["role"] = "Kepala Bagian"
            if item["status"] == "Process" and not item.get("is_verif", False):
                delete_ids.add(item["_id"])
            elif item["_id"] not in delete_ids:
                kepala_bagian_to_add.append(item)

        # Process sub_bag_transaksi
        sub_bag_to_add = []
        for item in sub_bag_transaksi:
            item["_id"] = str(item["_id"])
            item["role"] = "Sub Bagian"
            if not item.get("is_verif", False) and item["_id"] not in delete_ids:
                sub_bag_to_add.append(item)

        # Add the filtered kepala_bagian and sub_bag transactions
        all_transaksi["pengusulan"].extend(kepala_bagian_to_add)
        all_transaksi["pengusulan"].extend(sub_bag_to_add)

        # Process and add status to pengajuan_barang
        for item in staff_gudang:
            item["_id"] = str(item["_id"])
            item["role"] = "Staff Ruangan"
            all_transaksi["pengajuan_barang"].append(item)

        return all_transaksi

    except PyMongoError as e:
        error_message = f"MongoDB error: {str(e)}"
        return {"error": error_message}


@transaksi_bp.route("/", methods=["GET"])
def get_all_transaksi():
    data = fetch_transaksi_data()
    if "error" in data:
        return jsonify(data), 500
    return jsonify(data), 200


@transaksi_bp.route("/dashboard", methods=["GET"])
def get_dashboard():
    data = fetch_transaksi_data()
    if "error" in data:
        return jsonify(data), 500

    total_pengusulan = len(data["pengusulan"])
    total_pengajuan = len(data["pengajuan_barang"])
    total_transaksi = total_pengusulan + total_pengajuan

    dashboard_data = {
        "total_transaksi": total_transaksi,
        "total_pengusulan": total_pengusulan,
        "total_pengajuan": total_pengajuan,
        **data,
    }

    return jsonify(dashboard_data), 200


@transaksi_bp.route("/<string:transaksi_id>", methods=["GET"])
def get_detail_transaksi(transaksi_id):
    try:
        # Find the transaction by its _id
        transaction = mongo.db.transaksi.find_one({"_id": ObjectId(transaksi_id)})

        if not transaction:
            return jsonify({"error": "Transaction not found"}), 404

        # Convert ObjectId to string for JSON serialization
        transaction["_id"] = str(transaction["_id"])

        # Return the transaction details as JSON response
        return jsonify(transaction), 200

    except PyMongoError as e:
        error_message = f"MongoDB error: {str(e)}"
        return jsonify({"error": error_message}), 500


# @transaksi_bp.route("/decline", methods=["GET"])
# def get_declined_transaksi():
#     try:
#         # Find transactions where is_verif is False in either kepala_bagian or verifikasi
#         declined_items = []

#         kepala_bagian_declined = list(mongo.db.kepala_bagian.find({"is_verif": False}))
#         verifikasi_declined = list(mongo.db.verifikasi.find({"is_verif": False}))

#         declined_items.extend(kepala_bagian_declined)
#         declined_items.extend(verifikasi_declined)

#         for item in declined_items:
#             item["_id"] = str(item["_id"])
#         return jsonify({"declined_transaksi": declined_items}), 200

#     except PyMongoError as e:
#         error_message = f"MongoDB error: {str(e)}"
#         return jsonify({"error": error_message}), 500


# @transaksi_bp.route("/success", methods=["GET"])
# def get_successful_transaksi():
#     try:
#         # Find transactions where is_verif is True in verifikasi
#         successful_items = list(mongo.db.verifikasi.find({"is_verif": True}))
#         for item in successful_items:
#             item["_id"] = str(item["_id"])
#         return jsonify({"successful_transaksi": successful_items}), 200

#     except PyMongoError as e:
#         error_message = f"MongoDB error: {str(e)}"
#         return jsonify({"error": error_message}), 500


# @transaksi_bp.route("/on_process", methods=["GET"])
# def get_on_process_transaksi():
#     try:
#         # Find transactions where is_verif is False in sub_bag
#         on_process_items = list(mongo.db.sub_bag.find({"is_verif": False}))
#         for item in on_process_items:
#             item["_id"] = str(item["_id"])
#         return jsonify({"on_process_transaksi": on_process_items}), 200

#     except PyMongoError as e:
#         error_message = f"MongoDB error: {str(e)}"
#         return jsonify({"error": error_message}), 500

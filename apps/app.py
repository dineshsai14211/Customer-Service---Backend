import psycopg2
import random
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from db_connections.configuration import DATABASE_URL
from db_table.tables import db, CustomerInteractions
from log.log_switch import log_info, log_debug, log_error, log_warning

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL

# Initialize SQLAlchemy with the Flask app
db.init_app(app)


@app.route('/api/callback_request', methods=["POST"])
def callback_request():
    """
    Endpoint to create a new callback request.

    This function generates a unique request ID, creates a new record in the `CustomerInteractions` table
    with the data provided in the request payload, and commits the transaction to the database.

    :return: json
      A JSON object with status and message indicating success or failure, and the generated request ID.
    """
    log_info("callback_request function has started...")
    try:
        payload = request.get_json(force=True)
        request_id = None
        if not len(payload) >= 1:
            log_debug(f'No payload data')
            return jsonify(status="Failed", message="No payload data"), 400

        for item in payload:
            new_request_id = True
            while new_request_id:
                new_request_id = str(random.randint(1000, 9999))  # Generate a 4-digit random number
                if db.session.query(CustomerInteractions).filter_by(request_id=new_request_id).first() is None:
                    request_id = new_request_id
                    log_debug(f'New request_id has created = {request_id}')
                    break

            record = CustomerInteractions(customer_name=item["customer_name"],
                                          phone_number=item["phone_number"],
                                          request_type=item["request_type"],
                                          preferred_time=item["preferred_time"],
                                          request_id=request_id
                                          )

            db.session.add_all([record])
            log_debug(f'Records have been added with request_id = {request_id}')
        db.session.commit()
        return jsonify(status="Success", message="Callback request created", request_id=request_id), 200

    except Exception as err:
        log_error(err)
        return jsonify(Error=f'{err}'), 400
    finally:
        log_info("callback_request function has ended...")


# Customers Care Follows UP
@app.route('/api/callback_request/<int:request_id>', methods=["PUT"])
def customercare_callback_request(request_id):
    """
     Endpoint to update an existing callback request based on the request ID.

    This function updates the record in the `CustomerInteractions` table with additional information
    provided in the request payload. It verifies that the request ID exists and matches the customer name.

    :param request_id: int
      The ID of the request to update.
    :return:
      A JSON object with status and message indicating success or failure.
    """
    log_info(f'customercare_callback_request function has started...')
    try:
        result = db.session.query(CustomerInteractions).filter_by(request_id=str(request_id)).first()
        if result is None:
            log_debug(f'{request_id} has not found')
            return jsonify(status="Failed", message="Request ID not found,Check Once!"), 400

        payload = request.get_json(force=True)

        if result.customer_name != payload["customer_name"]:
            log_debug(f'customer_name associated with request_id not matched with name in payload')
            return jsonify(status="Failed",
                           message="customer_name associated with request_id not matched with name in payload"), 400

        result.additional_info = payload.get("additional_info")
        result.dealer_name = payload.get("dealer_name")
        result.dealer_phone_number = payload.get("dealer_phone_number")
        result.customer_status = "Processing"

        db.session.commit()
        log_debug(f'Updated the record associated with request_id={request_id}')
        return jsonify(status="Success", message="Callback request updated successfully"), 200

    except Exception as err:
        log_error(err)
        return jsonify(Error=f'{err}'), 400
    finally:
        log_info(f'customercare_callback_request function has ended...')


@app.route('/api/track', methods=["GET"])
def tracking_record():
    """
    Endpoint to track a callback request by request ID.

    This function retrieves a record from the `CustomerInteractions` table based on the request ID provided
    as a query parameter. It returns the details of the request if found.

    :return: json
    A JSON object with status and request details if successful, or an error message if not.
    """
    log_info(f'tracking_record function has started...')
    try:
        request_id = request.args.get("request_id")
        if len(request_id) != 4:
            log_debug(f'{request_id} - was wrong,check once again!')
            return jsonify(status="Failed", message="Request ID was wrong,check once again!"), 400

        result = db.session.query(CustomerInteractions).filter_by(request_id=request_id).first()
        if result is None:
            log_debug(f'{request_id} - has not found')
            return jsonify(status="Failed", message="Request ID not found,Check Once!"), 400

        log_debug(f'{result.to_dict()}')
        return jsonify(status="success",data=result.to_dict()), 200
    except Exception as err:
        log_error(err)
        return jsonify(Error=f'{err}'), 400
    finally:
        log_info(f'tracking_record function has ended...')


@app.route('/api/dealers/customer_info', methods=["GET"])
def dealers_tracking_customerinfo():
    """
    Retrieve customer information tracked by a dealer.

    This endpoint retrieves all records from the `CustomerInteractions` table that are associated with a
    specific dealer name provided as a query parameter.
    But response includes only the customer name, phone number, preferred time, additional information, and request type for each record.

    :return: json
     A JSON object with status and a list of customer details if records are found, or an error message if no records are found.
    """
    log_info(f'dealers_tracking_customerinfo function has started...')
    try:
        dealer = request.args.get("dealer_name")
        if dealer is None:
            log_debug(f'{dealer} - Dealer name should not be empty field ')
            return jsonify(status="Failed", message="Dealer name should not be empty field"), 400

        result = db.session.query(CustomerInteractions).filter(CustomerInteractions.dealer_name == dealer).all()
        if result:
            return_data = [{
                "customer_name": data.customer_name,
                "phone_number": data.phone_number,
                "additional_info": data.additional_info,
                "preferred_time": data.preferred_time,
                "request_type": data.request_type
            } for data in result]
            return jsonify(status="success", data=return_data), 200
        else:
            log_debug(f'{dealer} - No records found under these dealer name')
            return jsonify(status="Failed", message="No records found under these dealer name"), 400
    except Exception as err:
        log_error(err)
        return jsonify(Error=f'{err}'), 400
    finally:
        log_info(f'dealers_tracking_customerinfo function has ended...')


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

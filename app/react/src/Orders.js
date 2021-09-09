import React, { Fragment, useState, useEffect } from "react";
import ReactDOM from "react-dom";
import { HOST } from "./helper";
import OrderRow from "./components/OrderRow";

function Orders(props) {
  const [orders, setOrders] = useState({});

  const retrieveOrders = () => {
    fetch(HOST + "api/v1/order")
      .then((response) => response.json())
      .then((data) => {
        setOrders(data);
      });
  };

  useState(() => {
    retrieveOrders();
    const intervalId = setInterval(retrieveOrders, 10000);
    return () => clearInterval(intervalId);
  }, []);

  const handleDelivered = (order_id) => {
    fetch(HOST + "api/v1/order?order_id=" + order_id, { method: "DELETE" });
    setOrders(orders.filter((item) => item.id != order_id));
  };

  return (
    <div className="col-12">
      {Object.keys(orders).length > 0 ? (
        <div className="table-responsive mb-4">
          <table className="table table-striped">
            <thead>
              <tr>
                <th scope="col">Pedido</th>
                <th scope="col">Espera</th>
                <th scope="col">Pagamento</th>
                <th scope="col">Endereço</th>
                <th scope="col">Total</th>
                <th scope="col">Total Cliente</th>
                <th scope="col">Contato</th>
                <th scope="col">Confirmar entrega</th>
              </tr>
            </thead>
            <tbody>
              {orders.map((order) => (
                <OrderRow
                  handleDelivered={handleDelivered}
                  key={order.id}
                  order={order}
                />
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <h2 className="text-center mb-5">Não há pedidos a serem entregues</h2>
      )}
    </div>
  );
}

window.renderApp = (props) =>
  ReactDOM.render(
    <Orders {...props} />,
    document.getElementById("react-container")
  );

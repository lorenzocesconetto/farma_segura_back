import React from "react";
import moment from "moment";

moment.locale("pt-br");

export default function OrderRow(props) {
  const { handleDelivered, order } = props;
  return (
    <tr>
      <td>
        <a
          target="_blank"
          className="btn btn-warning"
          href={"/order/" + order.id}
        >
          {order.id}
        </a>
      </td>
      <td>{moment(order.placed_timestamp).fromNow()}</td>
      <td>{order.payment_method.name}</td>
      <td>
        {order.user.logradouro}, {order.user.complemento}
      </td>
      <td>R$ {order.total}</td>
      <td>R$ {order.frontend_total}</td>
      <td>
        <a
          target="_blank"
          className="btn btn-success"
          href={"http://api.whatsapp.com/send?phone=55" + order.user.phone}
        >
          <i
            style={{ fontSize: "1.6em" }}
            className="text-center align-middle fab fa-whatsapp"
          ></i>
          {"  "}
          {order.user.phone}
        </a>
      </td>
      <td>
        <button
          onClick={() => handleDelivered(order.id)}
          className="btn btn-info"
        >
          Entregue
        </button>
      </td>
    </tr>
  );
}

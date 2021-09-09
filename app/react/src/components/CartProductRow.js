import React, { Fragment, useState, useEffect } from "react";

export default function CartProductRow(props) {
  const { item, remove, updateCount } = props;
  // useEffect(() => {
  //   fetch(API_URL)
  //     .then((response) => response.json())
  //     .then((obj) => {
  //       setProduct({ ...obj });
  //     });
  // }, []);

  return (
    <tr>
      <td className="d-none d-sm-table-cell">
        <img height="70" src={item.img_small} alt="" />
      </td>
      <td>{item.name}</td>
      <td>R$ {item.price}</td>
      <td className="text-center">
        <div className="input-group">
          <div className="order-lg-1 order-md-3 order-3 input-group-prepend">
            <button
              onClick={() => {
                updateCount(item.id, item.quantity - 1);
              }}
              id="left-minus"
              className="btn btn-light text-secondary"
            >
              -
            </button>
          </div>
          <input
            className="order-lg-2 order-md-2 order-2"
            id="qty"
            value={item.quantity}
            min="1"
            name="quantity"
            type="number"
          />
          <div className="order-lg-3 order-md-1 order-1 input-group-append">
            <button
              id="right-plus"
              onClick={() => updateCount(item.id, item.quantity + 1)}
              className="btn btn-light text-secondary"
            >
              +
            </button>
          </div>
        </div>
      </td>
      <td className="text-center">
        <button
          onClick={() => remove(item.id)}
          className="btn btn-sm btn-danger"
        >
          <i className="fa fa-trash"></i>
        </button>
      </td>
    </tr>
  );
}

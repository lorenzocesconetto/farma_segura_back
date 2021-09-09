import React, { Fragment, useState, useEffect } from "react";
import ReactDOM from "react-dom";
import CartProductRow from "./components/CartProductRow";
import { loadState, saveState, HOST } from "./helper";

const API_URL = HOST + "api/v1/product?id=";

function Cart(props) {
  const [total, setTotal] = useState(0);
  const [cart, setCart] = useState(null);
  const [payment, setPayment] = useState(null);
  const [showMessage, setShowMessage] = useState(false);
  const [discount, setDiscount] = useState(0);
  const delivery = props["deliveryFee"];

  useEffect(() => {
    let discount = updateDiscount();
    updateTotal(discount);
  }, [cart]);

  // useEffect(() => {}, [discount]);

  useEffect(() => {
    const tmp_cart = loadState();
    for (let key in tmp_cart) {
      fetch(API_URL + key)
        .then((response) => response.json())
        .then((data) => {
          tmp_cart[key].name = data.name;
          tmp_cart[key].img_small = data.img_small;
          tmp_cart[key].price = data.price;
          tmp_cart[key].promotion_price = data.promotion_price;
          tmp_cart[key].promotion_qty = data.promotion_qty;
          setCart({ ...tmp_cart });
          saveState({ ...tmp_cart });
        });
    }
  }, []);

  const updateDiscount = () => {
    for (let key in cart) {
      let totalDiscount = 0;
      if (cart[key].promotion_price && cart[key].promotion_qty) {
        const priceDiff = cart[key].price - cart[key].promotion_price;
        const numDiscounterItems =
          Math.floor(cart[key].quantity / cart[key].promotion_qty) *
          cart[key].promotion_qty;
        totalDiscount += priceDiff * numDiscounterItems;
      }
      setDiscount(totalDiscount);
      return totalDiscount;
    }
  };
  const updateTotal = (discount) => {
    if (cart) {
      setTotal(
        delivery -
          discount +
          Object.keys(cart).reduce(
            (accumulator, key) =>
              accumulator + cart[key].price * cart[key].quantity,
            0
          )
      );
    }
  };

  const handlePayment = (e) => {
    setPayment(e.target.value);
  };

  const handleSubmit = () => {
    if (payment) {
      fetch(HOST + "api/v1/order", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          cart,
          payment,
          total,
        }),
      }).then((response) => {
        if (response.status === 200) {
          saveState({});
          window.location.href = HOST + "completed_order";
        } else if (response.status === 401) {
          window.location.href = HOST + "auth/login_msg";
        } else {
          window.location.href = HOST + "error";
        }
      });
    } else {
      setShowMessage(true);
    }
  };

  const updateCount = (id, count) => {
    let num = Math.max(1, count);
    num = Math.min(99, num);
    cart[id].quantity = num;
    setCart({ ...cart });
    saveState(cart);
  };

  const remove = (id) => {
    delete cart[id];
    setCart({ ...cart });
    saveState(cart);
  };

  return (
    <div className="container my-4 py-5">
      <div className="row">
        {cart && Object.keys(cart).length > 0 ? (
          <Fragment>
            <div className="col-12">
              <div className="table-responsive mb-4">
                <table className="table table-striped">
                  <thead>
                    <tr>
                      <th className="d-none d-sm-table-cell"></th>
                      <th scope="col">Produto</th>
                      <th scope="col">Preço Un.</th>
                      <th scope="col" className="text-center">
                        Un.
                      </th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {cart &&
                      Object.keys(cart).map((key) => (
                        <CartProductRow
                          key={key}
                          item={cart[key]}
                          remove={remove}
                          updateCount={updateCount}
                        />
                      ))}
                    <tr>
                      <td className="d-none d-sm-table-cell"></td>
                      <td></td>
                      <td>Taxa de entrega</td>
                      <td colSpan="2" className="text-right">
                        R$ {delivery.toFixed(2)}
                      </td>
                    </tr>

                    {discount > 0 && (
                      <tr>
                        <td className="d-none d-sm-table-cell"></td>
                        <td></td>
                        <td className="text-danger">Desconto</td>
                        <td colSpan="2" className="text-right text-danger">
                          R$ {discount.toFixed(2)}
                        </td>
                      </tr>
                    )}

                    <tr>
                      <td className="d-none d-sm-table-cell"></td>
                      <td></td>
                      <td>
                        <strong>Total</strong>
                      </td>
                      <td colSpan="2" className="text-right">
                        <strong>R$ {total.toFixed(2)}</strong>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            <div className="col mb-2">
              <div className="col text-center mb-4">
                <p>
                  OBS: Entrega em até 2h para pedidos feitos até 18:00. Após
                  esse horário, a entrega é feita no dia seguinte
                </p>
                {showMessage && (
                  <div className="alert alert-danger" role="alert">
                    Selecione um meio de pagamento abaixo
                  </div>
                )}
                <div className="mx-4 form-check form-check-inline">
                  <input
                    onChange={handlePayment}
                    checked={payment === "dinheiro"}
                    className="form-check-input"
                    type="radio"
                    id="inlineRadio1"
                    value="dinheiro"
                  />
                  <label className="form-check-label" htmlFor="inlineRadio1">
                    Dinheiro
                  </label>
                </div>
                <div className="mx-4 form-check form-check-inline">
                  <input
                    onChange={handlePayment}
                    checked={payment === "debito"}
                    className="form-check-input"
                    type="radio"
                    id="inlineRadio2"
                    value="debito"
                  />
                  <label className="form-check-label" htmlFor="inlineRadio2">
                    Cartão de débito (maquininha)
                  </label>
                </div>
                <div className="mx-4 form-check form-check-inline">
                  <input
                    onChange={handlePayment}
                    checked={payment === "credito"}
                    className="form-check-input"
                    type="radio"
                    id="inlineRadio3"
                    value="credito"
                  />
                  <label className="form-check-label" htmlFor="inlineRadio3">
                    Cartão de crédito (maquininha)
                  </label>
                </div>
              </div>
              <div className="row">
                <div className="col-sm-12 col-md-6">
                  <a href={HOST} className="btn btn-block btn-secondary mb-1">
                    Continuar comprando
                  </a>
                </div>
                <div className="col-sm-12 col-md-6 text-right">
                  <button
                    onClick={handleSubmit}
                    className="btn btn-lg btn-block btn-success text-uppercase"
                  >
                    Finalizar pedido
                  </button>
                </div>
              </div>
            </div>
          </Fragment>
        ) : (
          <div className="col-12 text-center" style={{ marginBottom: "15%" }}>
            <h2 className="mb-5">Você não tem produtos no seu carrinho</h2>
            <div className="mx-auto col-sm-12 col-md-6">
              <a href={HOST} className="btn btn-block btn-success">
                Continuar comprando
              </a>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

window.renderApp = (props) =>
  ReactDOM.render(
    <Cart {...props} />,
    document.getElementById("react-container")
  );

export const HOST =
  window.location.href.split("/")[0] +
  "//" +
  window.location.href.split("/")[2] +
  "/";

export const loadState = () => {
  try {
    const serializedState = localStorage.getItem("@cart");

    if (serializedState === "null" || serializedState === null) {
      localStorage.setItem("@cart", JSON.stringify({}));
      return {};
    }
    return JSON.parse(serializedState);
  } catch (err) {
    return undefined;
  }
};

export const saveState = (state) => {
  try {
    const serializedState = JSON.stringify(state);
    localStorage.setItem("@cart", serializedState);
  } catch {
    // ignore write errors
  }
};

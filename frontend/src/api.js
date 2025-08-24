
import axios from "axios";

const API = axios.create({
  baseURL: "https://gopal-tf8i.onrender.com/api",
});

export function setAuthToken(token) {
  if (token) {
    API.defaults.headers.common["Authorization"] = `Bearer ${token}`;
  } else {
    delete API.defaults.headers.common["Authorization"];
  }
}

export default API;

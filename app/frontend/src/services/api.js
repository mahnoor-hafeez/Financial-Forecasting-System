import axios from "axios";
const BASE_URL = "http://127.0.0.1:8000";

export const fetchData = async (symbol) => {
  try {
    const res = await axios.get(`${BASE_URL}/fetch-data/${symbol}`);
    return res.data;
  } catch (error) {
    console.error("API Error:", error);
    throw error;
  }
};

import { Outlet } from "react-router-dom";
import AppLayout from "./AppLayout";

export default function PrivateLayout() {
  const user = JSON.parse(localStorage.getItem("user") || "null");

  return (
    <AppLayout user={user}>
      <Outlet />
    </AppLayout>
  );
}

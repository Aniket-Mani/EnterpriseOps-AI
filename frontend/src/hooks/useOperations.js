import { useContext } from "react";
import { OperationsContext } from "../context/OperationsContext";

export function useOperations() {
  const context = useContext(OperationsContext);
  if (!context) throw new Error("useOperations must be used inside OperationsProvider");
  return context;
}

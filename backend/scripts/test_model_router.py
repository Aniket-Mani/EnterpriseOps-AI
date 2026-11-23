from app.agents.model_router import generate_response


if __name__ == "__main__":
    for task_type in ("routine", "complex"):
        print(f"\nTesting {task_type} task...")

        try:
            result = generate_response(
                "Reply with exactly: ROUTER_OK",
                task_type=task_type,
            )

            print("Success:", result["success"])
            print("Model used:", result["model"])
            print("Fallback used:", result["fallback_used"])
            print("Response:", result["text"])

        except Exception as exc:
            print("Failed:", type(exc).__name__, str(exc))
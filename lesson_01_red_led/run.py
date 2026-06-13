import helper
from my_program import my_program


def main() -> None:
    try:
        my_program()
    except ValueError as e:
        print(f"Input error: {e}")
    except RuntimeError as e:
        print(f"Hardware error: {e}")
    except KeyboardInterrupt:
        print("Stopped.")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        helper.cleanup()
        print("Cleanup complete.")


if __name__ == "__main__":
    main()

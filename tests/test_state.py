from src.state_of_things import State


class TestState:
    def test_name_defaults_to_classname(self):
        class TestNameDefault(State):
            pass

        assert TestNameDefault().name == "TestNameDefault"

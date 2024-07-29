import pytest
from src.state_of_things import State, Thing


class EnterExitTrackingState(State):
    """Records when a State is entered or exited."""

    def __init__(self) -> None:
        self.__entered_thing: Thing = None
        self.__exited_thing: Thing = None

    def enter(self, thing: Thing):
        self.__entered_thing = thing

    def exit(self, thing: Thing):
        self.__exited_thing = thing

    def assert_entered(self, thing: Thing):
        assert self.__entered_thing == thing

    def assert_not_entered(self):
        assert self.__entered_thing is None

    def assert_exited(self, thing: Thing):
        assert self.__exited_thing == thing

    def assert_not_exited(self):
        assert self.__exited_thing is None


class TestThing:

    def test_initial_state_is_entered(self):
        """Things must always enter an initial State when created."""
        initial_state = EnterExitTrackingState()
        thing = Thing(initial_state)

        assert thing.current_state == initial_state
        assert thing.previous_state is None

        initial_state.assert_entered(thing)
        initial_state.assert_not_exited()

    def test_initial_state_is_required(self):
        with pytest.raises(AssertionError) as expected_error:
            Thing(initial_state=None)

        assert str(expected_error.value) == "initial_state is required"

    def test_state_change_exits_and_enters_states(self):
        """
        When changing States, the current State should exit before
        the new State is entered.
        """
        initial_state = EnterExitTrackingState()
        new_state = EnterExitTrackingState()

        thing = Thing(initial_state)
        thing.go_to_state(new_state)

        assert thing.current_state == new_state
        assert thing.previous_state == initial_state

        initial_state.assert_exited(thing)
        new_state.assert_entered(thing)
        new_state.assert_not_exited()

    def test_going_to_current_state_does_not_change_state(self):
        """
        When changing States, if the new State is the same as the
        current State then do not enter or exit States.
        """
        initial_state = EnterExitTrackingState()

        thing = Thing(initial_state)

        # go to the current State (should not trigger a change)
        thing.go_to_state(initial_state)

        assert thing.current_state == initial_state
        assert thing.previous_state is None

        initial_state.assert_entered(thing)
        initial_state.assert_not_exited()

    # update - test time properties
    # update - test state staying the same
    # update - test state causing move to another state
    # time ellapsed and active
    # add missing pydocs

import pytest
from src.state_of_things import Thing
from .fixtures.state import *


class TestThing:

    def test_initial_state_is_entered_on_first_update(self):
        """Things must always enter an initial State on first update."""
        initial_state = EnterExitTrackingState()
        thing = Thing(initial_state)

        assert thing.current_state is None
        assert thing.previous_state is None

        thing.update()

        assert thing.current_state is initial_state
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

        new_state = EnterExitTrackingState()
        initial_state = ImmediateChangeState(next_state=new_state)

        thing = Thing(initial_state)
        # go to initial state, which then changes to the new state
        thing.update()

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
        initial_state = NeverChangeState()

        thing = Thing(initial_state)

        # go to the initial State (should not trigger a change)
        thing.update()

        assert thing.current_state == initial_state
        assert thing.previous_state is None

        initial_state.assert_entered(thing)
        initial_state.assert_not_exited()

    # update - test time properties
    # update - test state staying the same
    # update - test state causing move to another state
    # time ellapsed and active
    # add missing pydocs

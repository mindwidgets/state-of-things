from src.state_of_things import State, Thing, ThingObserver


class StateChangeObserver(ThingObserver):
    """Records when a state change is observed."""

    def __init__(self) -> None:
        self.__thing: Thing = None
        self.__old_state: State = None
        self.__new_state: State = None

    def state_changed(self, thing: Thing, old_state: State, new_state: State):
        self.__thing = thing
        self.__old_state = old_state
        self.__new_state = new_state

    def assert_notified(self, thing: Thing, old_state: State, new_state: State):
        assert self.__thing == thing
        assert self.__old_state == old_state
        assert self.__new_state == new_state

    def assert_not_notified(self):
        assert self.__thing is None
        assert self.__old_state is None
        assert self.__new_state is None


class CustomThingObserver(ThingObserver):
    """Records when a custom event is observed."""

    def __init__(self) -> None:
        self.__notified_v1: str = None
        self.__notified_v2: int = None

    def custom_event(self, v1: str, v2: int):
        self.__notified_v1 = v1
        self.__notified_v2 = v2

    def assert_notified(self, expected_v1: str, expected_v2: int):
        assert self.__notified_v1 == expected_v1
        assert self.__notified_v2 == expected_v2


class CustomNotifierState(State):
    """Notifies a custom event when entered."""

    EVENT_NAME = CustomThingObserver.custom_event.__name__

    def __init__(self, *params) -> None:
        self.params = params

    def enter(self, thing: Thing):
        thing.observers.notify(self.EVENT_NAME, *self.params)


class TestThingObservers:
    def test_state_change_notifies_attached_observers(self):
        """
        Observers that inherit from ThingObserver should receive
        notification of state changes with old and new States.
        """
        observers = [StateChangeObserver(), StateChangeObserver()]
        initial_state = State()
        new_state = State()

        thing = Thing(initial_state)
        # go to intial state
        thing.update()

        for observer in observers:
            thing.observers.attach(observer)

        thing.go_to_state(new_state)

        for observer in observers:
            observer.assert_notified(thing, initial_state, new_state)

    def test_custom_events_can_be_observed(self):
        """
        Observers may define custom events that Things and States can
        notify.
        """
        expected_v1 = "Hello custom event"
        expected_v2 = 12345

        # State will notify a custom event when entered
        custom_state = CustomNotifierState(expected_v1, expected_v2)

        thing = Thing(State())
        observer = CustomThingObserver()
        thing.observers.attach(observer)

        # trigger the custom event
        thing.go_to_state(custom_state)

        observer.assert_notified(expected_v1, expected_v2)

    def test_going_to_current_state_does_not_notify_change_state(self):
        """
        When changing States, if the new State is the same as the
        current State then do not notify a state change.
        """
        initial_state = State()

        thing = Thing(initial_state)
        observer = StateChangeObserver()
        thing.observers.attach(observer)

        # go to the current State (should not trigger a change)
        thing.go_to_state(initial_state)

        observer.assert_not_notified()

    def test_thing_observer_does_nothing_by_default(self):
        """
        By default, ThingObserver will do nothing when state changes
        are received (as opposed to throwing an exception).
        """
        observer = ThingObserver()

        observer.state_changed(Thing(State()), State(), State())

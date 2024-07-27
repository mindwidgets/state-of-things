from src.state_of_things import State, ThingObserver, Thing


class TestThing:

    def test_state_change_notifies_attached_observers(self):
        class StateChangeObserver(ThingObserver):
            def state_changed(self, old_state: State, new_state: State):
                self.old_state = old_state
                self.new_state = new_state

        observers = [StateChangeObserver(), StateChangeObserver()]
        first_state = State()
        second_state = State()

        thing = Thing(first_state)

        for observer in observers:
            thing.observers.attach(observer)

        thing.go_to_state(second_state)

        for observer in observers:
            assert observer.old_state == first_state
            assert observer.new_state == second_state

    def test_custom_thing_observers(self):
        class CustomThingObserver(ThingObserver):
            def custom_event(self, some_data: str):
                self.some_data = some_data

        initial_state = State()

        class CustomThingState(State):
            def enter(self, thing: Thing):
                thing.observers.notify("custom_event", "test")

        custom_state = CustomThingState()

        thing = Thing(initial_state)
        observer = CustomThingObserver()
        thing.observers.attach(observer)
        observer_without_event = ThingObserver()
        thing.observers.attach(observer_without_event)
        thing.go_to_state(custom_state)

        assert observer.some_data == "test"

    # test update of state and previous state
    # test update enter/exit
    # test time properties

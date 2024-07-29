import time
from .observers import Observers


class State:
    """
    Represents a State that a Thing can enter and exit. The State can
    transition a Thing into another State when it is updated.
    """

    @property
    def name(self):
        """The State's name, defaulting to the class name."""
        return type(self).__name__

    def enter(self, thing: "Thing"):
        """
        Called when a Thing enters this State. Typically used for
        one-time setup where State-specific context is added to the
        Thing.

        Args:
            thing (Thing): the Thing that entered this State.
        """
        pass

    def exit(self, thing: "Thing"):
        """
        Called when a Thing exists this State. Typically used to clean
        up resources initialized when the State is entered.

        Args:
            thing (Thing): the Thing that exited this State.
        """
        pass

    def update(self, thing: "Thing") -> "State":
        """
        Called periodically while a Thing is in this State. This
        function determines whether the Thing should remain in this
        State or change to another State.

        Often the Thing's time_ellapsed and time_active properties are
        referenced when a Thing should transition to another State after
        a given amount of time.

        Args:
            thing (Thing): the Thing to update in this State

        Returns:
            State: the next State for the Thing, or this State if the
            Thing should remain unchanged.
        """
        return self


class ThingObserver:
    """
    Implement the state_changed function of this class to receive
    notifications when a Thing changes State. All Thing observers
    should inherited from this class.

    Logging state changes to stdout is common for debugging purposes.
    """

    def state_changed(self, thing: "Thing", old_state: State, new_state: State):
        """
        Notified when a Thing changes from one State to another.

        Args:
            thing (Thing): the Thing that changed State.
            old_state (State): the State that the Thing exited.
            new_state (State): the State that the Thing entered.
        """
        pass


class Thing:
    """
    A Thing represents an object that can only be in one State at a
    time. It holds all global and per-State context needed by States to
    update and transition between States.

    Things can be manually set to a State via go_to_state, but ideally
    the States should internally manage the correct State for the Thing.
    """

    def __init__(self, initial_state: State, name: str = None):
        """
        Constructor that stores the initial State but does not change
        to it until update is called.

        Args:
            initial_state (State): the initial State for this Thing
            name (str, optional): the name of this Thing, usually for
            logging. Defaults to the class name.
        """
        assert initial_state, "initial_state is required"
        self.__initial_state = initial_state
        self.__name = name if name is not None else type(self).__name__

        self.__observers = Observers()

        self.__current_state: State = None
        self.__previous_state: State = None
        self.__time_last_update: float = 0
        self.__time_ellapsed: float = 0
        self.__time_active: float = 0

    def go_to_state(self, state: State):
        """
        Manually change the Thing to a new State. Notifies all observers
        of the State change if moving from a previous State.

        Args:
            state (State): the target State for this Thing
        """
        assert state, "state can not be None"

        # the State hasn't changed, don't do anything
        if self.__current_state == state:
            return

        # if changing from a previous State, exit it
        if self.__current_state:
            self.__current_state.exit(self)

        # update the Thing's state
        self.__previous_state = self.__current_state
        self.__current_state = state

        # only notify for change from initial state
        if self.__previous_state:
            self.observers.notify(
                "state_changed", self, self.__previous_state, self.__current_state
            )

        # reset time tracking properties
        self.__time_last_update = time.monotonic()
        self.__time_ellapsed = 0
        self.__time_active = 0

        # enter the new State
        self.__current_state.enter(self)

    def update(self):
        """
        Updates the time tracking properties of this Thing, and then
        updates the State. If the State update returns a new State,
        then this method calls go_to_state to change to it.
        """
        # if the Thing is not in it's initial State, change to it
        if self.__current_state is None:
            self.go_to_state(self.__initial_state)

        # update time tracking properties
        now = time.monotonic()
        self.__time_ellapsed = now - self.__time_last_update
        self.__time_last_update = now
        self.__time_active += self.__time_ellapsed

        # update the current State
        next_state = self.__current_state.update(self)
        if next_state != self.__current_state:
            self.go_to_state(next_state)

    @property
    def name(self) -> str:
        """
        Name of this Thing, defaulting to class name but can be
        manually set via the constructor.

        Returns:
            str: the name of this Thing.
        """
        return self.__name

    @property
    def current_state(self) -> State:
        """
        The current State of this Thing.

        Returns:
            State: the current State, or None if it does not have one.
        """
        return self.__current_state

    @property
    def previous_state(self) -> State:
        """
        The previous State of this Thing.

        Returns:
            State: the previous State, or None if it has not changed
            States.
        """
        return self.__previous_state

    @property
    def time_ellapsed(self) -> float:
        """
        The amount of time that has ellapsed since this Thing's last
        update call.

        Returns:
            float: the amount of ellapsed time, in seconds.
        """
        return self.__time_ellapsed

    @property
    def time_active(self) -> float:
        """
        The total amount of time that this Thing has been in the current
        State.

        Returns:
            float: the amount of time active in the current State, in
            seconds.
        """
        return self.__time_active

    @property
    def observers(self) -> Observers:
        """
        The observers that will be notified by this Thing. For instance,
        all observers that implement ThingObserver will be notified when
        this Thing changes State.

        Things can have custom observers that it's State implementations
        can notify as needed. For instance, a button Thing may have an
        observer that is notified when the button is pressed or
        released.

        Returns:
            Observers: this Thing's observers.
        """
        return self.__observers

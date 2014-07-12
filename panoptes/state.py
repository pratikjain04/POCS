"""@package panoptes.state
The StateMachine for the Panoptes Project. Inherits from smach (see ros.org).
"""
import smach

import panoptes.utils.logger as logger
import panoptes.utils.error as error

@logger.has_logger
class StateMachine(object):
    def __init__(self, observatory):
        """
        Initialize the StateMachine with an `Observatory`
        of the state into the `states` dict. Sets `current_state` to 'shutdown'

        @param  observatory     An instance of panoptes.observatory.Observatory
        """
        self.logger.info("Creating state machine")

        # Create a state machine container. The only outcome for our state machine is Parked,
        # otherwise machine keeps running
        self.sm = smach.StateMachine(outcomes=['parked'])

        # Attach the observatory to the state machine userdata
        self.sm.userdata.observatory = observatory

        # Open our state machine contained
        with self.sm:
            # Add states to the container
            smach.StateMachine.add('PARKED', Parked(), transitions={'shutdown': 'SHUTDOWN'})

            smach.StateMachine.add('SHUTDOWN', Shutdown(), transitions={'sleeping': 'SLEEPING'})

            smach.StateMachine.add('SLEEPING', Sleeping(), transitions={'parked': 'PARKED'})


    def execute(self):
        """
        Starts the execution of our state machine
        """
        self.logger.info("Beginning execution of state machine")
        outcome = self.sm.execute()
        return outcome

@logger.has_logger
class Parked(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['shutdown'])

    def execute(self, userdata):
        self.logger.info("Executing {}".format(self.__class__))
        return 'shutdown'

@logger.has_logger
class Shutdown(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['sleeping'])

    def execute(self, userdata):
        self.logger.info("Executing {}".format(self.__class__))
        return 'sleeping'

@logger.has_logger
class Sleeping(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['parked'])

    def execute(self, userdata):
        self.logger.info("Executing {}".format(self.__class__))
        return 'parked'
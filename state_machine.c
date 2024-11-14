#include<stdio.h>

typedef void (*stateFuncPtr)(void);

typedef enum transit_event{ 
    LAUNCH_COMPLETE_EVT,
    DETUMBLING_COMPLETE_EVT,
    DEPLOYMENT_COMPLETE_EVT,
    CRIT_BATTERY_EVT,
    LOW_CHARGE_EVT,
    ABOVE_COMMS_EVT,
    NOT_ABOVE_COMMS_EVT,
    DOING_RESEARCH_EVT,
    NOT_DOING_RESEARCH_EVT
} transit_event;

typedef struct fc_stm {
    stateFuncPtr curr_state;
    transit_event trig_event;
    stateFuncPtr next_state;

} fc_stm;

fc_stm = {
}





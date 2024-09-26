#include <stdio.h>
#include <string.h>
//import subsystem classes here?? 

//State string constants
//idk maybe unnecessary
const char* LAUNCHING_STRING = "Launching";
const char* DETUMBLING_STRING = "Detumbling";
const char* IDLE_WITH_SUN_STRING = "Idle With Sun";
const char* IDLE_WITHOUT_SUN_STRING = "Idle Without Sun";
const char* PAYLOAD_STRING  = "Payload";
const char* DOWNLINK_STRING = "Downlink";
const char* LOW_POWER_STRING = "Low Power";
const char* SLEEP_STRING = "Sleep";
const char* QUICK_HEAT_STRING = "Quick Heat";

//States as integers
//necessary for switch statement?
const int LAUNCHING_INDEX = 0;
const int DETUMBLING_INDEX = 1;
const int IDLE_WITH_SUN_INDEX = 2;
const int IDLE_WITHOUT_SUN_INDEX = 3;
const int PAYLOAD_INDEX  = 4;
const int DOWNLINK_INDEX = 5;
const int LOW_POWER_INDEX = 6;
const int SLEEP_INDEX = 7;
const int QUICK_HEAT_INDEX = 8;







//Defining input variables

//how will sunstate be determined? Will this be a string or state index?
int sunState = 0;
//create function that converts power level to percentage if not already?
float state_of_charge = 0;
//how will events be scheduled?
int desiredState = 0;
//idk how this is measured in one var?
float wherePointing = 0;
//hawt
float temp = 0;

//solar pannel vars
int solar_pwr = 0;




/////////////////////////////////////////////ARE GLOBAL VARIABLES A GOOD IDEA OR SHOULD THESE BE PUT IN MAIN????\\\\\\\\\\\\\\\\\\\\\\\\\\\


//Defining subsystems 
//will these be passed in or.... idk what these are gonna look like
// using typdef rn just cuz no want error
typedef IMU;
typedef reactionWheels;
typedef magnetorquers;
typedef sidkiqZ2;
typedef payload;


//state functions
void launching(void){
    //launching shenanigans
}

void detumbling(void){
    // detumbling shenanigans
}

void idle_with_sun(void){
    // idle_with_sun shenanigans
}

void idle_without_sun(void){
    // idle_without_sun shenanigans
}

void using_payload(void){
    // payload shenanigans
}

void downlink(void){
    // downlink shenanigans
}

void low_power(void){
    //low_power shenanigans
}

void sleep(void){
    // honk-shoooo
}

void quick_heat(void){
    //oooooooo its cold in here, there must...
}


////////////////////////////////////////////////BIG IMPORTANT STATE SET FUNCTION\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ 

int set_state(sunState, powerLevel, desiredState, wherePointing, temp) {
    //logic for picking states go here
    return LAUNCHING_INDEX;
}

//idk if this will work or if there needs to be seperate update methods with return values for each variable
void update_vars(){
    int sunState = 0;   
    float powerLevel = 0;
    int desiredState = 0;
    float wherePointing = 0;
    float temp = 0;
}

int main() {


    while(1){
        update_vars(sunState, state_of_charge, desiredState, wherePointing, temp);
        //get the current state from set_state
        int current_state = set_state(sunState, state_of_charge, desiredState, wherePointing, temp);

        // matches the index returned by set_state to the correct state index
        switch (current_state){
            case LAUNCHING_INDEX:
                launching();
                break;
            case DETUMBLING_INDEX:
                detumbling();
                break;
            case IDLE_WITH_SUN_INDEX:
                idle_with_sun();
                break;
            case IDLE_WITHOUT_SUN_INDEX:
                idle_without_sun();
                break;
            case PAYLOAD_INDEX:
                using_payload();
                break;
            case DOWNLINK_INDEX:
                downlink();
                break;
            case LOW_POWER_INDEX:
                low_power();
                break;
            case SLEEP_INDEX:
                sleep();
                break;
            case QUICK_HEAT_INDEX:
                sleep();
                break;
        }
    }
    return 0;
}



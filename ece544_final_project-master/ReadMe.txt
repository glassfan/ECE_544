AutomatedRobotCanRetrieval Project ReadMe
    This project attempted to design a robot that would detect a can of a certain color
    and retrieve that can, detect a target location, and deposit that can at the target 
    location.

    The robot platform consisted of an Actobotics Junior Runt Rover, PYNQ ARM+Zynq development board,
    an Actobotics Gripper Arm, a Web Cam, and a WiFi dongle.

    All of the physicals were constructed successfully and the robot was able to manually perform all the
    motions expected of it.  It did run into physical failure due to motors failing (specifically the metal to plastic wheel hubs).
    The can detection classifiers were able to sucessfully identify cans and targets.

    The robot integration was unsuccessful, as we never were able to get the robot to perform an automated can retrieval.

Directory Listing:
    <repository_head>                                                       - Top level repository directory
        Classifier_Design                                                   - Files related to training and testing the can detection classifier
            cam_classifier.py
            can_lbp2.xml
            can_lbp.xml
            cascade.xml
            find_can.py
            haar2.xml
            pull_urls.py
            webcam_test.py

        Documents                                                           - Project Documentation
            AutomatedRoboticCanRetrievalDesignReport.pdf                    - Final Design Report describing the project (submitted June 9, 2017)
            AutomatedRoboticCanRetrievalProgressReport.pdf                  - Project Progress Report (submitted June 2, 2017)
            AutomatedRoboticCanRetrievalProposal.pdf                        - Project Proposal (submitted May 21, 2017)
            AutomatedRoboticsCanRetrievalSlides.pdf                         - Project Presentation Slides (presented June 7, 2017)

        Jupyter_Notebooks                                                   - Jupyter Notebooks demonstating PYNQ functionality
            can_detect.ipynb                                                - Can detection and integration notebook (unfinished)
            gripper_demo.ipynb                                              - Demonstration of Gripper control using servo PWM signaling
            Robot_Control_GPIO.ipynb                                        - Demonstration of robot motor controls using GPIO outputs for motor enable/direction
            Robot_Controller_Class_Demo.ipynb                               - Demonstration of integrated robot controller class (used in project demo)

        Pmod_HB3_C_driver                                                   - PMOD_HB3 C driver attempt (unsuccessful)
            pmod_hb3                                                        - PMOD_HB3 PMOD IOP directory (copied and modified from PMOD_PWM)
                Debug                                                       - Debug directory is where the make files and ELF/Binary results are stored
                    makefile                                                - Makefile required adjustment to point to the PMOD_HB3 sources
                    objects.mk                      
                    pmod_hb3.bin                                            - Final Binary file used to communicate with the Python module
                    pmod_hb3.elf
                    pmod_hb3.elf.size
                    sources.mk                                              - File used by the Makefile to list the project sources
                    src
                        pmod_hb3.d  
                        pmod_hb3.o
                        subdir.mk                                           - Second level of make file listings
                src                                                         - Source directory for the PMOD_HB3 project
                    lscript.ld                                              - Linker file, unchanged from PMOD_PWM design
                    pmod_hb3.c                                              - Custom C driver design that attempted to integrate the GPIO and PWM functionality for a single PMOD (unsuccessful)
            pmod_hb3.bin                                                    - Copy of the binary file produced from the custom C driver design
            pmod_hb3.py                                                     - Custom python application utilizing the custom C driver design to attempt to control the PMOD HB3 motor controller

        RobotControllerClass
            robot_controller.py                                             - Final working robot controller design using the PMOD_IO design to manage the GPIO connection to the motors and
                                                                            -   the PMOD_PWM design to manage control of the gripper arm


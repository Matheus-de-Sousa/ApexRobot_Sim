execute_process(COMMAND "/home/matheus/Documents/Apex_ws/build/apex_controller/catkin_generated/python_distutils_install.sh" RESULT_VARIABLE res)

if(NOT res EQUAL 0)
  message(FATAL_ERROR "execute_process(/home/matheus/Documents/Apex_ws/build/apex_controller/catkin_generated/python_distutils_install.sh) returned error code ")
endif()

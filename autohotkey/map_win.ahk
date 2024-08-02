Capslock::LControl ; make Caps Lock the control button 
LControl::Capslock

+F11:: 
RUN ControlMyMonitor.exe /SetValue Primary 60 17, D:\Tools\controlmymonitor 
return


ReleaseStandby()
{
	try
	    Run  "D:\tools\RAMMap\RAMMap64.exe -Et"
	catch
	    MsgBox "script not work"
}

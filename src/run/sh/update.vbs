Dim wsh
Set wsh = WScript.CreateObject("WScript.Shell")

Dim fso
Set fso = CreateObject("Scripting.FileSystemObject")


DesktopPath = wsh.SpecialFolders("Desktop")

UpdatePath = "C:\mysoft_update"


'清除老程序进程
wsh.Run "taskkill /f /im mysoft.exe",0
WScript.Sleep(2000)


'删除老程序
If  fso.fileExists(DesktopPath & "\mysoft.exe") Then
    fso.DeleteFile(DesktopPath & "\mysoft.exe")
	WScript.Sleep(2000)
End If


'复制新程序到桌面
If  fso.fileExists(UpdatePath & "\mysoft.exe") Then
    fso.CopyFile UpdatePath & "\mysoft.exe", DesktopPath & "\mysoft.exe"
	WScript.Sleep(2000)
End If


'运行新程序
If  fso.fileExists(DesktopPath & "\mysoft.exe") Then
    wsh.Run   DesktopPath &"\mysoft.exe",false,false
End If


'最后的处理
Set fso=NoThing
WScript.quit

Set wsh=NoThing
WScript.quit

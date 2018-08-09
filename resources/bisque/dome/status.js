/* Java Script */
Out = JSON.stringify({
    "connected": sky6Dome.IsConnected,
    "coupled": sky6Dome.IsCoupled,
    "moving": !sky6Dome.IsGotoComplete,
    "slit": sky6Dome.slitState(),
});
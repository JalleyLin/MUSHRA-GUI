import beyond.Reaper.Direct
import beyond.Reaper.Settings
import beyond.Network


try:

  with beyond.Network.Client(beyond.Reaper.Settings.External_Program_Address) as Client:

    Active = True
    while Active:

      l = Client.Receive()

      try:
        exec(l[0])
      except Exception as e:
        import traceback
        e.Traceback = traceback.extract_tb(e.__traceback__)
        l = e

      Client.Send(l)
      
except Exception as e: Say(e)
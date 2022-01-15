import unittest
import utilities

class TestStringMethods(unittest.TestCase):

    def test_roomcreate(self):
        utilities.delete_room("Howdy1");
        #clean out

        roomsBeforeCall =  utilities.count_rooms();
        utilities.create_room({"room" : "Howdy1"});
        roomsAfterCall = utilities.count_rooms();
        utilities.delete_room("Howdy1");
        self.assertEqual(roomsBeforeCall + 1, roomsAfterCall);

        

    def test_roomdelete(self):
        utilities.delete_room("Howdy2");
        #clean out

        utilities.create_room({"room" : "Howdy2"});
        roomsBeforeCall =  utilities.count_rooms();
        utilities.delete_room("Howdy2");
        roomsAfterCall = utilities.count_rooms();
        self.assertEqual(roomsBeforeCall - 1, roomsAfterCall);
        
    
    def test_createMultipleRooms(self):

        utilities.delete_room("Yabba");
        utilities.delete_room("Dabba");
        utilities.delete_room("Doo");
        utilities.delete_room("Badoo");
        #clean out

        roomsBeforeCall =  utilities.count_rooms();
        utilities.create_room({"room": "Yabba"});
        utilities.create_room({"room": "Dabba"});
        utilities.create_room({"room": "Doo"});
        utilities.create_room({"room": "Badoo"});
        roomsAfterCall =  utilities.count_rooms();
        utilities.delete_room("Yabba");
        utilities.delete_room("Dabba");
        utilities.delete_room("Doo");
        utilities.delete_room("Badoo");
        self.assertEqual(roomsBeforeCall, roomsAfterCall-4);



if __name__ == '__main__':
    unittest.main()
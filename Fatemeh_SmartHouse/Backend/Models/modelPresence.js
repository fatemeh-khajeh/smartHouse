const mongoose = require('mongoose');  

const presenceSchema =  mongoose.Schema({
    name:String,
    datetime:String,
    entries:String,
    photo:String
    
    
});

module.exports = mongoose.model('presence', presenceSchema);


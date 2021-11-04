const express = require('express');
const cors = require('cors');  
const app = express();
app.use(cors());

const mongoose = require('mongoose');
const connection = mongoose.connection;

var bodyParser = require('body-parser'); 
const Presence = require('./Models/modelPresence');
app.use(bodyParser.json());                            
app.use(bodyParser.urlencoded({ extended: true })); 

//mongoose.connect('mongodb://localhost:27017/presenceDb',{ useUnifiedTopology: true, useNewUrlParser: true });
//mongoose.connect('mongodb+srv://fkhajeh:fkhajeh@clusterfatemeh.bme0i.mongodb.net/smartHouseDB?retryWrites=true&w=majority',({ useUnifiedTopology: true, useNewUrlParser: true } )); // baraye estefade dar MongoAtlas # baraye peida kardan in ode dar ghesmat collections/commandlinetools/connect instruction/connect your application
mongoose.connect('mongodb+srv://fkhajeh:fkhajeh@clusterfatemeh.bme0i.mongodb.net/smartHouseDb?retryWrites=true&w=majority',({ useUnifiedTopology: true, useNewUrlParser: true } ));
const PORT = 3116;
app.listen(PORT,()=>{                                  
    console.log("j'écoute le port 3116!!");
});                                                     

connection.once('open',()=>{
    console.log("connected to MongoDb");
});

 app.post('/presence',(req, res)=>{                  
    console.log('req.body', req.body);             
    const presenceAdd = new Presence(req.body);        
    presenceAdd.save((err, presenceAdd)=>{                 
        if(err){
            return res.status(500).json(err);           
        }
        res.status(201).json(presenceAdd);                
    });
}); 

app.get('/presenceAll',(req,res)=>{
    Presence.find()
    .exec()
    .then(presence => res.status(200).json(presence));
});

 
app.delete('/delImage/:id', (req,res)=>{
    const id = req.params.id;
    Presence.findByIdAndDelete(id,(err,user)=>{
        if(err){
            return res.status(500).json(err);
        }
        res.status(202).json({ msg:`l'image'avec l'id ${user._id} suprimee`});
    });
});

app.put('/updateUser/:name', (req, res) => { 
    const name = req.params.name;
    //Presence.findByIdAndUpdate(id,req.body,(err,presence)=>{
    Presence.findOneAndUpdate(name, req.body,(err,presence)=>{
        if(err){
            return res.status(500).json(err);
        }
        res.status(202).json({ msg:` informations d'entrée d'utilisateur  avec le nom  ${presence.name} mis a jour`});
    });
});

// app.put('/updateUser/:name', (req, res) => { 
//     var query = {'name': req.params.name};
//     req.newData.name = req.user.name;

//     MyModel.findOneAndUpdate(query, req.newData, {upsert: true}, function(err, doc) {
//         if (err) return res.send(500, {error: err});
//         return res.send('Succesfully saved.');
//     });
// });
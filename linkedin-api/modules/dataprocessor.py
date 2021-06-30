import pandas as pd
import sys
import json
# future
import asyncio


class Decomposer():

    def __init__(self, d):
        try:

            data = d.replace("\\n", "")
            # data = data.replace(" ", "")
            data = data.replace("\\", " ")
            data = json.loads(data)
            # self._dictdata = pd.read_json(data)

            # del data["data"]["$deletedFields"]

            self._dictdata = pd.Series(data["included"])
            # print(self._dictdata)
            self._un = pd.Series(data["data"])
            # print(self._un)
        except:
            print("error>>init::", sys.exc_info()[1])

    def _delefuc(self):
        for i in range(len(self._dictdata)):
            del self._dictdata[i]["$deletedFields"]

    async def _process(self, future, value):
        ser = list()
        k = self._dictdata.copy()
        for i in k:
            if value == i["$type"]:
                ser.append(i)
        future.set_result(ser)

    async def _skill(self, future, value):
        skill = list()
        for i in value:
            try:
                skill.append(i["name"])
            except:
                pass
        future.set_result(skill)

    async def _publication(self, future, value):
        pub = list()
        templist = ["name", "publisher", "description", "url"]
        for i in value:
            temp = {}
            for j in templist:
                try:
                    temp[j] = i[j]
                except:
                    temp[j] = None
            pub.append(temp)
        future.set_result(pub)

    async def _pos(self, future, value):
        postion = list()
        templist = ["locationName", "title", "companyName", "description"]
        for i in value:
            temp = {}
            for j in templist:
                try:
                    temp[j] = i[j]
                except:
                    temp[j] = None
            postion.append(temp)
        future.set_result(postion)

    async def _summary(self, future, value, imagevalue):

        temp = {}
        templist = ["industryName", "lastName", "locationName", "birthDate", "firstName", "summary", "headline"]
        for i in value:
            for j in templist:
                try:
                    temp[j] = i[j]
                except:
                    temp[j] = None
        try:
            temp["image"] = imagevalue[0]["masterImage"]
        except:
            temp["image"] = None
        future.set_result(temp)

    async def _education(self, future, value):
        edu = list()
        templist = ["description", "degreeName", "schoolName", "fieldOfStudy"]
        for i in value:
            temp = {}
            for j in templist:
                try:
                    temp[j] = i[j]
                except:
                    temp[j] = None
            edu.append(temp)
        future.set_result(edu)

    async def _Organization(self, future, value):
        org = list()
        templist = ["description", "position"]
        for i in value:
            temp = {}
            for j in templist:
                try:
                    temp[j] = i[j]
                except:
                    temp[j] = None
            org.append(temp)
        future.set_result(org)

    async def _Honor(self, future, value):
        honor = list()
        templist = ["description", "position", "title", "issuer"]
        for i in value:
            temp = {}
            for j in templist:
                try:
                    temp[j] = i[j]
                except:
                    temp[j] = None
            honor.append(temp)
        future.set_result(honor)

    async def _Language(self, future, value):
        Language = list()
        templist = ["name", "proficiency"]
        for i in value:
            temp = {}
            for j in templist:
                try:
                    temp[j] = i[j]
                except:
                    temp[j] = None
            Language.append(temp)
        future.set_result(Language)

    async def _Certification(self, future, value):
        Certification = list()
        templist = ["authority", "name"]
        for i in value:
            temp = {}
            for j in templist:
                try:
                    temp[j] = i[j]
                except:
                    temp[j] = None
            Certification.append(temp)
        future.set_result(Certification)

    def startfunc(self):
        # self._delefuc()
        maindict = {}
        values = [
            "com.linkedin.voyager.identity.profile.Profile",
            "com.linkedin.common.Date",
            "com.linkedin.voyager.identity.profile.Position",
            "com.linkedin.voyager.identity.profile.Education",
            "com.linkedin.voyager.identity.profile.Skill",
            "com.linkedin.voyager.identity.profile.Publication",
            "com.linkedin.voyager.identity.profile.Project",
            "com.linkedin.voyager.identity.profile.Organization",
            "com.linkedin.voyager.identity.profile.Honor",
            "com.linkedin.voyager.identity.profile.Language",
            "com.linkedin.voyager.identity.profile.Certification",
            "com.linkedin.voyager.identity.profile.Course",
            "com.linkedin.voyager.identity.profile.TestScore",
            "com.linkedin.voyager.identity.profile.Picture"
        ]
        # loop = asyncio.get_event_loop()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        futuredict = {}
        datadict = {}
        for i in values:
            futuredict[i] = asyncio.Future()
        for i in futuredict.keys():
            asyncio.ensure_future(self._process(future=futuredict[i], value=i))
            loop.run_until_complete(futuredict[i])

        for i in values:
            datadict[i] = futuredict[i].result()
        # print(ujson.dumps(datadict))
        # loop.close()
        # all future
        skillfuture = asyncio.Future()
        publicationfuture = asyncio.Future()
        posfuture = asyncio.Future()
        summeryfuture = asyncio.Future()
        edufuture = asyncio.Future()
        orgfuture = asyncio.Future()
        horfuture = asyncio.Future()
        lngfuture = asyncio.Future()
        cerfuture = asyncio.Future()
        # all ensure future
        print(datadict)
        asyncio.ensure_future(self._skill(future=skillfuture,
                                          value=datadict["com.linkedin.voyager.identity.profile.Skill"]))
        asyncio.ensure_future(self._Certification(future=cerfuture,
                                                  value=datadict["com.linkedin.voyager.identity.profile.Certification"]))
        asyncio.ensure_future(self._publication(future=publicationfuture,
                                                value=datadict["com.linkedin.voyager.identity.profile.Publication"]))
        asyncio.ensure_future(self._pos(future=posfuture,
                                        value=datadict["com.linkedin.voyager.identity.profile.Position"]))
        asyncio.ensure_future(self._summary(future=summeryfuture,
                                            value=datadict["com.linkedin.voyager.identity.profile.Profile"],
                                            imagevalue=datadict["com.linkedin.voyager.identity.profile.Picture"]))
        asyncio.ensure_future(self._education(future=edufuture,
                                              value=datadict["com.linkedin.voyager.identity.profile.Education"]))
        asyncio.ensure_future(self._Organization(future=orgfuture,
                                                 value=datadict["com.linkedin.voyager.identity.profile.Organization"]))
        asyncio.ensure_future(self._Honor(future=horfuture,
                                          value=datadict["com.linkedin.voyager.identity.profile.Honor"]))
        asyncio.ensure_future(self._Language(future=lngfuture,
                                             value=datadict["com.linkedin.voyager.identity.profile.Language"]))
        # loop complete
        loop.run_until_complete(skillfuture)
        loop.run_until_complete(lngfuture)
        loop.run_until_complete(orgfuture)
        loop.run_until_complete(edufuture)
        loop.run_until_complete(summeryfuture)
        loop.run_until_complete(posfuture)
        loop.run_until_complete(publicationfuture)
        loop.run_until_complete(cerfuture)
        loop.run_until_complete(horfuture)
        maindict["skill"] = skillfuture.result()
        maindict["language"] = lngfuture.result()
        maindict["organization"] = orgfuture.result()
        maindict["education"] = edufuture.result()
        maindict["summary"] = summeryfuture.result()
        maindict["position"] = posfuture.result()
        maindict["publication"] = publicationfuture.result()
        maindict["certificate"] = cerfuture.result()
        maindict["honor"] = horfuture.result()
        # loop.close()
        return (maindict)


if __name__ == '__main__':
    pass
    # d = Decomposer()
    # d.startfunc()